#include <filesystem>
#include <iostream>

#include <framework/disable_all_warnings.h>
DISABLE_WARNINGS_PUSH()
#include <glm/common.hpp>
#include <glm/vec3.hpp>
DISABLE_WARNINGS_POP()
#include <framework/image.h>
#include "progressbar.hpp"

const std::filesystem::path resources_dir_path { RESOURCES_DIR };
const std::filesystem::path out_dir_path { OUTPUT_DIR };

constexpr float D = 0.97f;
constexpr float K = 0.4375f;
constexpr uint32_t ITER_LIMIT = 1000U;

Image<glm::uvec3> toUint(const Image<glm::vec3>& values) {
    Image<glm::uvec3> uintValues = Image<glm::uvec3>(values.width, values.height);
    #pragma omp parallel for
    for (int32_t y = 0; y < values.height; y++) {
        #pragma omp parallel for
        for (int32_t x = 0; x < values.width; x++) { 
            const glm::vec3& pixel = values.safeAccess(x, y, NEAREST);
            uintValues.data[uintValues.getImageOffset(x, y)] = glm::uvec3(pixel.x, pixel.y, pixel.z);
        }
    }
    return uintValues;
}

Image<glm::vec3> toFloat(const Image<glm::uvec3>& values) {
    Image<glm::vec3> floatValues = Image<glm::vec3>(values.width, values.height);
    #pragma omp parallel for
    for (int32_t y = 0; y < values.height; y++) {
        #pragma omp parallel for
        for (int32_t x = 0; x < values.width; x++) { 
            const glm::uvec3& pixel = values.safeAccess(x, y, NEAREST);
            floatValues.data[floatValues.getImageOffset(x, y)] = glm::vec3(pixel.x, pixel.y, pixel.z);
        }
    }
    return floatValues;
}

Image<bool> flagValue(const Image<glm::uvec3>& values, const glm::uvec3 desiredValue) {
    Image<bool> equalityMask = Image<bool>(values.width, values.height);
    #pragma omp parallel for
    for (int32_t y = 0; y < values.height; y++) {
        #pragma omp parallel for
        for (int32_t x = 0; x < values.width; x++) {
            const glm::uvec3 pixel = values.safeAccess(x, y, NEAREST);
            equalityMask.data[equalityMask.getImageOffset(x, y)] = glm::all(glm::equal(pixel, desiredValue));
        }
    }
    return equalityMask;
}

Image<glm::uvec3> iterativeInterpolation(const Image<glm::uvec3>& values, const glm::uvec3 unknown_value = {255U, 255U, 255U}) {
    Image<bool> toInterp                = flagValue(values, unknown_value);
    Image<glm::vec3> interpolatedArray  = toFloat(values);
    Image<glm::vec3> velocities(values.width, values.height);

    std::cout << "Interpolating..." << std::endl;
    progressbar bar(ITER_LIMIT);
    uint32_t iteration = 0U;
    while (iteration++ < ITER_LIMIT) {
        // Copy over previous values
        Image<glm::vec3> previousVelocities = velocities;
        Image<glm::vec3> previousField      = interpolatedArray;

        #pragma omp parallel for
        for (int32_t y = 0; y < values.height; y++) {
            #pragma omp parallel for
            for (int32_t x = 0; x < values.width; x++) {
                size_t imageOffset = values.getImageOffset(x, y);

                // Skip pixel if value is known
                if (!toInterp.data[imageOffset]) { continue; }

                // Acquire previous field values
                const glm::vec3& previousValue = previousField.data[imageOffset];
                const glm::vec3& up            = previousField.safeAccess(x, y - 1, NEAREST);
                const glm::vec3& down          = previousField.safeAccess(x, y + 1, NEAREST);
                const glm::vec3& left          = previousField.safeAccess(x - 1, y, NEAREST);
                const glm::vec3& right         = previousField.safeAccess(x + 1, y, NEAREST);

                // Compute new velocity and field value
                const glm::vec3& previousVelocity   = previousVelocities.data[imageOffset];
                const glm::vec3 velocity            = (D * previousVelocity) + (K * (up + down + left + right - (4.0f * previousValue)));
                const glm::vec3 value               = previousValue + velocity;

                // Assign new values to running arrays
                velocities.data[imageOffset]        = velocity;
                interpolatedArray.data[imageOffset] = value;
            }
        }
        bar.update();
    }

    return toUint(interpolatedArray);
}

int main(int argc, char* argv[]) {
    const std::string fileName      = "cat-edge-normals.png";
    Image<glm::uvec3> input         = Image<glm::uvec3>(resources_dir_path / fileName);
    Image<glm::uvec3> output        = iterativeInterpolation(input);
    output.writeToFile(out_dir_path / "result.png");

    return EXIT_SUCCESS;
}
