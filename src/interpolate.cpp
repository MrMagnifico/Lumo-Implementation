#include <filesystem>
#include <iostream>

#include <framework/disable_all_warnings.h>
DISABLE_WARNINGS_PUSH()
#include <glm/common.hpp>
#include <glm/vec3.hpp>
DISABLE_WARNINGS_POP()
#include <framework/image.h>
#include "progressbar.hpp"

const std::filesystem::path resources_dir_path{RESOURCES_DIR};
const std::filesystem::path out_dir_path{OUTPUT_DIR};

constexpr float MAX_PIXEL_DISTANCE = 65025.0f; // 255^2
constexpr float MAX_PIXEL_VALUE = 255.0f;
constexpr float D = 0.97f;
constexpr float K = 0.4375f;
constexpr uint32_t ITER_LIMIT = 1000U;

Image<glm::uvec3> toUint(const Image<glm::vec3> &values, bool denormalise = false)
{
    Image<glm::uvec3> uintValues = Image<glm::uvec3>(values.width, values.height);
#pragma omp parallel for
    for (int32_t y = 0; y < values.height; y++)
    {
#pragma omp parallel for
        for (int32_t x = 0; x < values.width; x++)
        {
            glm::vec3 pixel = values.safeAccess(x, y, NEAREST);
            if (denormalise) { pixel = (pixel * 127.5f) + 127.5f; }
            uintValues.data[uintValues.getImageOffset(x, y)] = glm::uvec3(pixel.x, pixel.y, pixel.z);
        }
    }
    return uintValues;
}

Image<glm::vec3> toFloat(const Image<glm::uvec3> &values, bool normalise = false)
{
    Image<glm::vec3> floatValues = Image<glm::vec3>(values.width, values.height);
    #pragma omp parallel for
    for (int32_t y = 0; y < values.height; y++)
    {
    #pragma omp parallel for
        for (int32_t x = 0; x < values.width; x++)
        {
            const glm::uvec3 &pixel = values.safeAccess(x, y, NEAREST);
            glm::vec3 pixelFloat(pixel.x, pixel.y, pixel.z);
            if (normalise) { pixelFloat = (pixelFloat - 127.5f) / 127.5f; }
            floatValues.data[floatValues.getImageOffset(x, y)] = pixelFloat;
        }
    }
    return floatValues;
}

/**
 * Create boolean image marking areas where a particular value exists
 *
 * @param values Image of values where particular values should be flagged
 * @param desiredValue Value to be flagged
 *
 * @return Boolean image where locations in which desiredValue was found in values are marked true; false otherwise
 */
Image<bool> flagValue(const Image<glm::uvec3> &values, const glm::uvec3 desiredValue)
{
    Image<bool> equalityMask = Image<bool>(values.width, values.height);
#pragma omp parallel for
    for (int32_t y = 0; y < values.height; y++)
    {
#pragma omp parallel for
        for (int32_t x = 0; x < values.width; x++)
        {
            const glm::uvec3 pixel = values.safeAccess(x, y, NEAREST);
            equalityMask.data[equalityMask.getImageOffset(x, y)] = glm::all(glm::equal(pixel, desiredValue));
        }
    }
    return equalityMask;
}

/**
 * Make the vector represented by the RGB values of the input image unit by adjusting the z-axis (green) value
 *
 * @param values Image of RGB values
 * @param inputNormalised Indicates if the inputs are normalised (i.e. values between 0 and 1).
 * It is assumed that values are in the range [0, 255] otherwise
 */
void unitizeRGB(Image<glm::vec3> &values, bool inputNormalised = false)
{
    const float maxValue = inputNormalised ? 1.0f : MAX_PIXEL_DISTANCE;
#pragma omp parallel for
    for (int32_t y = 0; y < values.height; y++)
    {
#pragma omp parallel for
        for (int32_t x = 0; x < values.width; x++)
        {
            glm::vec3 &pixel = values.data[values.getImageOffset(x, y)];
            pixel.b = std::sqrt(maxValue - (pixel.r * pixel.r) - (pixel.g * pixel.g));
        }
    }
}

/**
 * Perform sparse interpolation using a simple iterative dampened-spring diffuser
 *
 * @param values Sparse image containing values to be interpolated
 * @param unknown_value Pixels having this RGB value are the unknown pixels whose values will be obtained via interpolation; all others are ignored
 * @param normaliseIntermediate Normalise the intermediate data (i.e divide RGB values by 255)
 * @param unitizeOutput Ensure that the output vectors represented by each pixel are unit length (or 255 in case of no normalisation)
 * @param saveIntermediate Save intermediate interpolation results and velocities as PNG files in the output directory
 *
 * @return Image with pixels having unknown_value interpolated from known pixels
 */
Image<glm::uvec3> iterativeInterpolation(const Image<glm::uvec3> &values,
                                         const glm::uvec3 unknown_value = {255U, 255U, 255U},
                                         const bool normaliseIntermediate = false,
                                         const bool unitizeOutput = false,
                                         const bool saveIntermediate = false)
{
    Image<bool> toInterp = flagValue(values, unknown_value);
    Image<glm::vec3> interpolatedArray = toFloat(values, normaliseIntermediate);
    Image<glm::vec3> velocities(values.width, values.height);

    progressbar bar(ITER_LIMIT);
    uint32_t iteration = 0U;
    while (iteration++ < ITER_LIMIT)
    {
        // Copy over previous values
        Image<glm::vec3> previousVelocities = velocities;
        Image<glm::vec3> previousField = interpolatedArray;

#pragma omp parallel for
        for (int32_t y = 0; y < values.height; y++)
        {
#pragma omp parallel for
            for (int32_t x = 0; x < values.width; x++)
            {
                size_t imageOffset = values.getImageOffset(x, y);

                // Skip pixel if value is known
                if (!toInterp.data[imageOffset])
                {
                    continue;
                }

                // Acquire previous field values
                const glm::vec3 &previousValue = previousField.data[imageOffset];
                const glm::vec3 &up = previousField.safeAccess(x, y - 1, NEAREST);
                const glm::vec3 &down = previousField.safeAccess(x, y + 1, NEAREST);
                const glm::vec3 &left = previousField.safeAccess(x - 1, y, NEAREST);
                const glm::vec3 &right = previousField.safeAccess(x + 1, y, NEAREST);

                // Compute new velocity and field value
                const glm::vec3 &previousVelocity = previousVelocities.data[imageOffset];
                const glm::vec3 velocity = (D * previousVelocity) + (K * (up + down + left + right - (4.0f * previousValue)));
                const glm::vec3 value = previousValue + velocity;

                // Assign new values to running arrays
                velocities.data[imageOffset] = velocity;
                interpolatedArray.data[imageOffset] = value;
            }
        }
        bar.update();

        if (saveIntermediate)
        {
            const std::filesystem::path velocityPath = out_dir_path / "velocities_interm" / (std::to_string(iteration) + ".png");
            const std::filesystem::path fieldPath = out_dir_path / "fields_interm" / (std::to_string(iteration) + ".png");
            toUint(interpolatedArray, normaliseIntermediate).writeToFile(fieldPath); // Looks weird if not converted to uint first
            velocities.writeToFile(velocityPath);                                    // This one is fine though for some reason
        }
    }

    if (unitizeOutput)
    {
        unitizeRGB(interpolatedArray, normaliseIntermediate);
    }
    return toUint(interpolatedArray, normaliseIntermediate);
}

// 1: file path
// 2: file name
// 3 4 5: R G B
// 6: normalise intermediate (0 or 1)
// 7: optional extra path
int main(int argc, char *argv[])
{
    std::vector<std::string> args(argv, argv + argc);

    Image<glm::uvec3> input     = Image<glm::uvec3>(std::filesystem::path(args[1]) / (args[2] + ".png"));
    bool normaliseIntermediate  = argc > 6 ? std::stoi(args[6]) : false;

    std::cout << "Interpolating " << args[2] << ":" << std::endl;
    Image<glm::uvec3> output = iterativeInterpolation(input, glm::vec3(std::stoi(args[3]), std::stoi(args[4]), std::stoi(args[5])),
                                                      normaliseIntermediate, true, false);
    std::cout << std::endl;

    std::filesystem::path outPath = out_dir_path;

    if (argc > 7)
        outPath = out_dir_path / args[7];

    output.writeToFile(outPath / (args[2] + "-interp.png"));

    return EXIT_SUCCESS;
}
