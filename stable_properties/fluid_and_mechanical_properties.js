const math = require('mathjs');
/**
 * Importing Data from "fluid_and_mechanical_properties" File
 * 
 * Usage:
 * const data = require('./fluid_and_mechanical_properties);
 * 
 * Description:
 * This module demonstrates how to import data from a file named "fluid_and_mechanical_properties"
 * using the `require` statement in JavaScript. Make sure the file is in the same directory as
 * your script or provide the correct path to the file.
 * 
 * 
 */



/**
 * {fluidProperties} = require('./fluid_and_mechanical_properties)
 * Object containing properties of various fluids.
 * Each fluid is represented as a key with an object containing its properties:
 * - sg: Specific gravity
 * - mu: Dynamic viscosity (Pa.s)
 * - Cp: Specific heat capacity (kJ/kg.K)
 * - Tfreeze: Freezing temperature (°C)
 * - Tboil: Boiling temperature (°C)
 */
const fluidProperties = {
    "water": {
        "specificGravity": 1,
        "viscosity": 0.001,
        "specificHeatCapacity": 1,
        "freezingTemperature": 0,
        "boilingTemperature": 100
    },
    "mercury":{
        "specificGravity": 13.546,
        "viscosity": 1.526*10**(-3),
        "specificHeatCapacity": 0.14,
        "freezingTemperature":  -38.83,
        "boilingTemperature": 356.73
    },
    "gasoline": {
        "specificGravity": 0.72,
        "viscosity": 0.00029,
        "specificHeatCapacity": 2.22,
        "freezingTemperature": -50,
        "boilingTemperature": 150
    },
    "diesel": {
        "specificGravity": 0.8,
        "viscosity": 0.0022,
        "specificHeatCapacity": 2.05,
        "freezingTemperature": -60,
        "boilingTemperature": 300
    },
    "benzene": {
        "specificGravity": 0.88,
        "viscosity": 0.0006,
        "specificHeatCapacity": 1.19,
        "freezingTemperature": 5.5,
        "boilingTemperature": 80
    },
    "ethanol": {
        "specificGravity": 0.79,
        "viscosity": 0.0012,
        "specificHeatCapacity": 2.4,
        "freezingTemperature": -114,
        "boilingTemperature": 78.4
    },
    "acetone": {
        "specificGravity": 0.78,
        "viscosity": 0.003,
        "specificHeatCapacity": 2.15,
        "freezingTemperature": -95,
        "boilingTemperature": 56
    },
    "corn oil": {
        "specificGravity": 0.92,
        "viscosity": 0.02,
        "specificHeatCapacity": 1.9,
        "freezingTemperature": -11,
        "boilingTemperature": 245
    },
    "glycerine": {
        "specificGravity": 1.26,
        "viscosity": 0.95,
        "specificHeatCapacity": 2.43,
        "freezingTemperature": 17.8,
        "boilingTemperature": 290
    },
    "honey": {
        "specificGravity": 1.4,
        "viscosity": 10,
        "specificHeatCapacity": 2.52,
        "freezingTemperature": -10,
        "boilingTemperature": 80
    }
};

/**const {materialProperties} = require('./fluid_and_mechanical_properties)
 * Object containing properties of various materials.
 * Each material is represented as a key with an object containing its properties:
 * - sg: Specific gravity
 * - Es: Elastic modulus range (GPa)
 * - sults: Ultimate tensile strength range (MPa)
 * - linexp: Linear expansion coefficient (µm/m.°C)
 * - nud: Poisson's ratio
 * - Cp: Specific heat capacity (kJ/kg.K)
 */
let materialProperties = {
    "aluminum alloy": {
        "specificGravity": 2.7,
        "elasticModulusRange": [70, 80],
        "ultimateTensileStrengthRange": [310, 550],
        "linearExpansionCoefficient": 23,
        "poissonsRatio": 0.33,
        "specificHeatCapacity": 0.9
    },
    "steel alloy": {
        "specificGravity": 7.7,
        "elasticModulusRange": [195, 210],
        "ultimateTensileStrengthRange": [550, 1400],
        "linearExpansionCoefficient": 12,
        "poissonsRatio": 0.30,
        "specificHeatCapacity": 0.42
    },
    "copper": {
        "specificGravity": 7.7,
        "elasticModulusRange": [195, 210],
        "ultimateTensileStrengthRange": [550, 1400],
        "linearExpansionCoefficient": 12,
        "poissonsRatio": 0.30,
        "specificHeatCapacity": 0.386
    },
    "brass": {
        "specificGravity": 8.4,
        "elasticModulusRange": [96, 110],
        "ultimateTensileStrengthRange": [300, 590],
        "linearExpansionCoefficient": 20,
        "poissonsRatio": 0.34,
        "specificHeatCapacity": 0.380
    }
};
/**const {getFluidProperties} = require('./fluid_and_mechanical_properties)
 * Retrieves the properties of a specified fluid and adjusts units if necessary.
 * Only import this module if you require fluid_mechanical properties for calculations
 * @param {string} material - The name of the fluid.
 * @param {number} unitSelection - The unit selection (0 for SI, 1 for Imperial).
 * @returns {Object} The properties of the fluid, with adjusted units if specified.
 */
const getFluidProperties = (material, unitSelection) => {
    // Retrieve fluid properties for the specified material
    let fluid = fluidProperties[material];

    // Check if the fluid properties exist and if the latentHeat property is defined
    if (fluid) {
        // Check the unit selection and adjust properties accordingly
        if (unitSelection === "si") {
            // Convert density from specific gravity to kg/m³
            fluid.density = fluid.specificGravity * 1000;
            // Convert latent heat to SI unit (kJ/kg)
            fluid.latentHeat = fluid.latentHeat;
        } else if (unitSelection === "uscs") {
            // Convert density from specific gravity to lb/ft³
            fluid.density = fluid.specificGravity * 62.4;
            // Convert dynamic viscosity to lb/ft·s
            fluid.viscosity = fluid.viscosity * 0.672;
            // Convert specific heat capacity to BTU/(lb·°F)
            fluid.specificHeat = Math.round(100 * fluid.specificHeatCapacity * 0.239) / 100;
            // Convert latent heat to Imperial unit (BTU/lb)
            fluid.latentHeat = fluid.latentHeat * 0.000430209214; // Convert kJ/kg to BTU/lb
        }
    } else {
        console.error(`Fluid properties for "${material}" or latentHeat property not defined.`);
    }

    return fluid;
};

/**const {getMaterialProperties} = require('./fluid_and_mechanical_properties)
 * Retrieves the properties of a specified material and adjusts units if necessary.
 * Only import this module if you require fluid_mechanical properties for calculations
 * @param {string} material - The name of the material.
 * @param {number} unitSelection - The unit selection (0 for SI, 1 for Imperial).
 * @returns {Object} The properties of the material, with adjusted units.
 */
const getMaterialProperties = (material, unitSelection) => {
    let properties = { ...materialProperties[material] };
    
    // Assign other material properties
    const poissonsRatio = properties.poissonsRatio;
    let specificHeatCapacity = properties.specificHeatCapacity;
    const shearModulus = properties.elasticModulus / (2 * (1 + poissonsRatio));
    
    // Add latent heat of fusion property dynamically
    if (material === 'ice') {
        // Latent heat of fusion for ice in J/kg
        properties.latentHeat = 334000;
    }
    
    // Check the unit selection and adjust properties accordingly
    if (unitSelection === 1) {
        // Convert values to Imperial units
        specificHeatCapacity = Math.round(specificHeatCapacity * 0.239 * 100) / 100;
        properties.elasticModulus *= 145037.737734 * 1e-6;
        properties.shearModulus *= 145037.737734 * 1e-6;
        properties.ultimateTensileStrength *= 145.037738 * 1e-3;
    }

    properties.specificHeatCapacity = specificHeatCapacity;

    return properties;
}

/**
 * Thermal Properties of Substances Data Structure
 *
 * This data structure stores the thermal properties of various substances.
 * Each substance is an object with the following properties:
 * 
 * Properties:
 * - meltingPoint: The temperature at which the substance transitions from solid to liquid (in degrees Celsius).
 * - specificLatentHeatOfFusion: The amount of heat required to change the substance from solid to liquid 
 *                               at constant temperature (in joules per kilogram).
 * - boilingPoint: The temperature at which the substance transitions from liquid to gas (in degrees Celsius).
 * - specificLatentHeatOfVaporisation: The amount of heat required to change the substance from liquid to gas 
 *                                      at constant temperature (in joules per kilogram).
 *
 * Each property is keyed by the substance's name with its values represented in an object. 
 * The data structure is designed for easy access to the thermal properties for various calculations 
 * in physics and chemistry involving phase changes.
 *
 * Example Usage:
 * let heatFusion = substanceThermalProperties['water'].specificLatentHeatOfFusion;
 * let boilingPointEthanol = substanceThermalProperties['ethanol'].boilingPoint;
 *
 * Note:
 * The data provided should be used considering standard atmospheric pressure conditions and 
 * the accuracy is subject to the purity of the substances.
 */
const substanceThermalProperties = {
    "water": {
        "meltingPoint": 0,
        "specificLatentHeatOfFusion": 3.36 * 10**5,
        "boilingPoint": 100,
        "specificLatentHeatOfVaporisation": 2.26 * 10**6
    },
    "mercury": {
        "meltingPoint": -39,
        "specificLatentHeatOfFusion": 1.14 * 10**4,
        "boilingPoint": 357,
        "specificLatentHeatOfVaporisation": 2.96 * 10**5
    },
    "ethanol": {
        "meltingPoint": -114,
        "specificLatentHeatOfFusion": 1.08 * 10**5,
        "boilingPoint": 78,
        "specificLatentHeatOfVaporisation": 8.55 * 10**5
    },
    "gold": {
        "meltingPoint": 1063,
        "specificLatentHeatOfFusion": 6.28 * 10**4,
        "boilingPoint": 2808,
        "specificLatentHeatOfVaporisation": 1.72 * 10**6
    },
    "copper": {
        "meltingPoint": 1083,
        "specificLatentHeatOfFusion": 2.07 * 10**5,
        "boilingPoint": 2566,
        "specificLatentHeatOfVaporisation": 4.73 * 10**6
    },
    "lead": {
        "meltingPoint": 327,
        "specificLatentHeatOfFusion": 2.32 * 10**4,
        "boilingPoint": 1750,
        "specificLatentHeatOfVaporisation": 8.59 * 10**5
    },
    "nitrogen": {
        "meltingPoint": -210,
        "specificLatentHeatOfFusion": 2.57 * 10**4,
        "boilingPoint": -196,
        "specificLatentHeatOfVaporisation": 2.00 * 10**5
    },
    "oxygen": {
        "meltingPoint": -219,
        "specificLatentHeatOfFusion": 1.39 * 10**4,
        "boilingPoint": -183,
        "specificLatentHeatOfVaporisation": 2.13 * 10**5
    }
};

const getSubstanceThermalProperties = (material, unitSelection) => {
    // Retrieve fluid properties for the specified material
    let property = substanceThermalProperties[material];

    // Check if the fluid properties exist
    if (property) {
        // Check the unit selection and adjust properties accordingly
        if (unitSelection === "si") {
            return property;
        } else if (unitSelection === "uscs") {
            // Convert specific latent heat to Imperial unit (BTU/lbm)
            property.specificLatentHeatOfFusion = property.specificLatentHeatOfFusion * 0.000429922614; // Convert kJ/kg to BTU/lbm
            property.specificLatentHeatOfVaporisation = property.specificLatentHeatOfVaporisation * 0.000429922614;
            // Convert From Celsius to Fahrenheit
            property.boilingPoint = (property.boilingPoint * 9/5) + 32;
            property.meltingPoint = (property.meltingPoint * 9/5) + 32;

            return property;
        }
    } else {
        console.error(`Material properties for "${material}" not found.`);
        return null; // Or return an appropriate error object/message
    }
};




module.exports = {
    fluidProperties,
    materialProperties,
    getMaterialProperties,
    getFluidProperties,
    getSubstanceThermalProperties, // Updated to camelCase
    substanceThermalProperties
}
    