/**
 * UnitConverter Class Documentation
 * 
 * The UnitConverter class provides functionality for converting units across various measurement systems including length, weight, speed, time, pressure, force, and angles. It also supports generating random values within specified or custom ranges for these units.
 * 
 * Constructor:
 * Initializes the class with predefined conversion rates and ranges for supported units in categories such as length, weight, speed, time, pressure, force, and angles.
 * 
 * Usage:
 * To use the UnitConverter class, instantiate it and utilize its methods to convert units or generate random values within specified ranges. The class is designed to support a wide range of units across different measurement categories.
 * 
 * How to Use Efficiently:
 * 1. Import the UnitConverter class into your JavaScript file:
 *    - Use the require statement to import the class from the 'UnitConverter' file.
 *      Example: const UnitConverter = require('./UnitConverter');
 *      Make sure the 'UnitConverter' file is in the same directory as your script or provide the correct path to the file.
 * 2. Instantiate the UnitConverter class: const converter = new UnitConverter();
 * 3. To convert a value from one unit to another:
 *    - Use the convert method: converter.convert(value, fromUnit, toUnit);
 *      Example: converter.convert(10, 'm', 'km') // Converts 10 meters to kilometers.
 * 4. To generate a random value for a specific unit:
 *    - Use the generateRandomValueForUnit method: converter.generateRandomValueForUnit(unit, relationship, custom_range);
 *      - unit: Specify the unit for which you want to generate a random value.
 *      - relationship (optional): Specify the relationship between two generated values. For instance, 'greater' to generate a value greater than another generated value.
 *      - custom_range (optional): Specify a custom range within which the random value should fall.
 *      Example: converter.generateRandomValueForUnit('m', 'greater', [0, 100]) // Generates a random value greater than 0 and less than 100 meters.
 * 
 * Note: Make sure to check the supported units in each category and provide valid units as arguments to the methods.
 */

const math = require('mathjs');

class UnitConverter {
    constructor() {
        this.conversionRates = {
            length: {
                'm': { rate: 1, range: [1, 1000] },
                'km': { rate: 1000, range: [10, 15] }, // Kilometers
                'miles': { rate: 1609.34, range: [10, 15] }, // Miles
                'ft': { rate: 0.3048, range: [1, 5280] }, // Feet
                'inches': { rate: 0.0254, range: [0.0254, 2.54] }, // Inches
                'cm': { rate: 0.01, range: [0.01, 1] }, // Centimeters
                'mm': { rate: 0.001, range: [0.001, 0.1] }, // Millimeters
                'µm': { rate: 1e-6, range: [1e-6, 1e-4] }, // Micrometers (Microns)
                'nm': { rate: 1e-9, range: [1e-9, 1e-7] }, // Nanometers
            },
            weight: {
                kilograms: { rate: 1, range: [1, 100] },
                grams: { rate: 1000, range: [100, 100000] },
                pounds: { rate: 2.20462, range: [0.2, 220.462] }
            },
            speed: {
                'm/s': { rate: 1, range: [1, 40] },
                'km/h': { rate: 3.6, range: [800, 880] },
                'mph': { rate: 2.23694, range: [500, 600] },
                'ft/s': { rate: 3.28084, range: [1, 145] } // ft/s, assuming range
            },
            time: {
                'seconds': { rate: 1, range: [1, 360] },
                'minutes': { rate: 60, range: [0.8, 1.2] },
                'hours': { rate: 3600, range: [0.1, 1] } // Equivalent to 1 to 2 minutes
            },
            pressure: {
                'Pa': { rate: 1, range: [100, 100000] }, // Pascal, base unit for pressure
                'kPa': { rate: 1000, range: [100, 100000] },
                'MPa': { rate: 100000, range: [100, 100000] },
                'GPa': { rate: 100000000, range: [100, 100000] },
                'psi': { rate: 6894.76, range: [0.145038, 14503.8] }, // Pounds per square inch
                'bar': { rate: 100000, range: [1, 1000] }, // Bar, commonly used in atmospheric pressure readings
                'atm': { rate: 101325, range: [0.986923, 986.923] }, // Standard atmosphere, average sea-level pressure
                'Torr': { rate: 133.322, range: [1, 760] }, // Torr, nearly equivalent to the millimeter of mercury (mmHg)
                'mmHg': { rate: 133.322, range: [1, 760] } // Millimeters of mercury, commonly used in medical and meteorological fields
            },
            force: {
                "N": { rate: 1, range: [100, 100000] }, // Newtons
                "kN": { rate: 1000, range: [0.1, 100] }, // Kilonewtons
                "lbf": { rate: 4.44822, range: [22.4809, 22480.9] }, // Pounds-force
                "MN": { rate: 1e6, range: [0.0001, 100] } // Meganewtons
            },
            energy: {
                "J": { rate: 1, range: [1, 1000000] }, // Joules
                "kJ": { rate: 1000, range: [0.001, 1000] }, // Kilojoules
                "cal": { rate: 4.184, range: [0.239, 239005.736] }, // Calories
                "kcal": { rate: 4184, range: [0.000239, 239.005736] }, // Kilocalories
                "BTU": { rate: 1055.06, range: [0.000947817, 947.81712] }, // British Thermal Units
                "ftlb": { rate: 1.35582, range: [0.737562, 737562.149] }, // Foot-pounds
            },
            power: {
                "W": { rate: 1, range: [1, 1000000] }, // Watts
                "kW": { rate: 1000, range: [0.001, 1000] }, // Kilowatts
                "MW": { rate: 1000000, range: [0.000001, 1000] }, // Megawatts
                "HP": { rate: 745.7, range: [0.001341022, 1341.022] }, // Horsepower
            },          
            angles: {
                "rad": {rate: 1, range: [0.5, 1.0]}, //  range in radians
                "deg": {rate:  math.pi/180, range: [15, 60]} //range in degrees
            }
        }
    };
    /**
     * 
     * Converts a given value from one unit to another within the supported categories.
     * 
     * @param {number} value The value to convert.
     * @param {string} fromUnit The unit of the given value.
     * @param {string} toUnit The target unit for conversion.
     * @returns {number} The converted value in the target unit.
     * @throws {Error} If the conversion between the specified units is not supported.
     */
    convert(value, fromUnit, toUnit) {
        let fromRate = null;
        let toRate = null;
        let standard_rate = null;

        // Iterate through the categories to find the units
        for (const category in this.conversionRates) {
            standard_rate = this.conversionRates[category][fromUnit]
            if (this.conversionRates[category][fromUnit]) {
                fromRate = this.conversionRates[category][fromUnit].rate; // Corrected to fetch fromUnit's rate
            }
            if (this.conversionRates[category][toUnit]) {
                toRate = this.conversionRates[category][toUnit].rate;
            }
        }
        // If both rates are found, perform the conversion
        if (fromRate !== null && toRate !== null) {
            return value * fromRate / toRate;
        } else {
            // If we can't find the units, throw an error
            throw new Error(`Conversion from ${fromUnit} to ${toUnit} is not supported.`);
        }
    }

    /**
     * Generates a random value for the specified unit within its predefined or custom range.
     * Optionally considers a relationship ('smaller' or 'larger') between two generated values.
     * 
     * @param {string} unit The unit for which to generate a random value.
     * @param {string} relationship Optional. Specifies the relationship between two values ('None', 'smaller', 'larger').
     * @param {Array<number>} custom_range Optional. A custom range [min, max] to override the predefined range.
     * @returns {number|Object} A random value within the specified range, or an object with two values if a relationship is specified.
     * @throws {Error} If the specified unit is not supported or if an invalid relationship is provided.
     */
    generateRandomValueForUnit(unit, relationship = "None", custom_range = null) {
        const categories = Object.keys(this.conversionRates);
        for (let category of categories) {
            const units = this.conversionRates[category];
            if (units[unit]) {
                // Use the custom range if provided, otherwise use the default range.
                const range = custom_range || units[unit].range;
                
                let value_1 = Math.random() * (range[1] - range[0]) + range[0];
                let value_2 = Math.random() * (range[1] - range[0]) + range[0];
    
                if (relationship === "None") {
                    return value_1; // If no relationship is specified, return a single value.
                } else if (relationship === "smaller" || relationship === "larger") {
                    if ((relationship === "smaller" && value_1 > value_2) || (relationship === "larger" && value_1 < value_2)) {
                        [value_1, value_2] = [value_2, value_1]; // Swap to ensure correct relationship.
                    }
                    return { value_1, value_2 }; // Return both values in an object for both cases.
                } else {
                    throw new Error(`Invalid relationship "${relationship}". Must be 'None', 'smaller', or 'larger'.`);
                }
            }
        }
        throw new Error(`Unit ${unit} is not supported.`);
    }
    
    
}
module.exports = {
    UnitConverter
};

// converter = new UnitConverter()
// console.log(converter.convert(5,"km","ft"))
v_1 = 5
v1_converted = converter.convert('speed', 'km/h', 'm/s', v1);
