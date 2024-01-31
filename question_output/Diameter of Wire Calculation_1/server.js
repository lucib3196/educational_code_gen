const math = require('mathjs');

function convertMPaToPa(stressMPa) {
    return stressMPa * Math.pow(10, 6); // Convert MPa to Pa
}

const generate = () => {
    const unitSystems = {
        si: {
            force: 'N',
            stress: 'MPa',
            distance: 'mm'
        }
    };

    // 1. Dynamic Parameter Selection
    // For simplicity, we're using SI units only in this example.
    const units = unitSystems.si;

    // 3. Value Generation
    const tensileForce = math.randomInt(50, 101); // Tensile force between 50 and 100 N
    const stress = math.random(2, 5, true); // Stress between 2 and 5 MPa

    // Convert stress to Pa for calculation
    const stressPa = convertMPaToPa(stress);

    // 4. Solution Synthesis
    // Using the formula: stress = force / area, and area = (pi * d^2) / 4
    // Rearrange to solve for d: d = sqrt((4 * force) / (pi * stress))
    const diameter = Math.sqrt((4 * tensileForce) / (Math.PI * stressPa)) * 1000; // Convert m to mm

    // Return the structured data
    return {
        params: {
            tensileForce: tensileForce,
            stress: stress,
            unitsForce: units.force,
            unitsStress: units.stress,
            unitsDist: units.distance
        },
        correct_answers: {
            diameter: math.round(diameter, 3) // Round to 3 decimal places
        },
        nDigits: 3,
        sigfigs: 3
    };
};

module.exports = {
    generate
};