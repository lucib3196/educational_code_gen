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
    if (fluid && fluid.latentHeat !== undefined) {
        // Check the unit selection and adjust properties accordingly
        if (unitSelection === 0) {
            // Convert density from specific gravity to kg/m³
            fluid.density = fluid.specificGravity * 1000;
            // Convert latent heat to SI unit (kJ/kg)
            fluid.latentHeat = fluid.latentHeat;
        } else {
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




module.exports = {
    fluidProperties,
    materialProperties,
    getMaterialProperties,
    getFluidProperties
}