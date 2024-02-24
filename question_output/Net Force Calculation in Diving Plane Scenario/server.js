
const math = require('mathjs');

/**
 * The ForceConverter class provides static methods to convert forces between
 * different units: newtons (N), pounds-force (lbf).
 */
class ForceConverter {
    /**
     * Converts force from newtons to pounds-force.
     * 
     * @param {number} forceN - The force in newtons.
     * @return {number} The force in pounds-force.
     */
    static NtoLbf(forceN) {
        return forceN * 0.224809;
    }

    /**
     * Converts force from pounds-force to newtons.
     * 
     * @param {number} forceLbf - The force in pounds-force.
     * @return {number} The force in newtons.
     */
    static LbftoN(forceLbf) {
        return forceLbf / 0.224809;
    }
}

const generate = () => {
    // Dynamic Parameter Selection
    const unitSystems = {
        si: {
            force: 'N',
            mass: 'kg',
            acceleration: 'm/s^2'
        },
        uscs: {
            force: 'lbf',
            mass: 'lb',
            acceleration: 'ft/s^2'
        }
    };

    const selectedSystem = math.randomInt(0, 2) === 0 ? 'si' : 'uscs';
    const units = unitSystems[selectedSystem];

    // Value Generation
    const mass = math.randomInt(50, 101); // Mass of the pilot
    const g = 9.81; // Gravitational acceleration in m/s^2
    const n = 5; // Acceleration in terms of g

    // Calculating the force in Newtons
    let forceN = mass * n * g;

    // Appropriate Transformations
    let forceConverted;
    switch (selectedSystem) {
        case "si":
            forceConverted = forceN; // No conversion needed for SI units
            break;
        case "uscs":
            // Converting mass to pounds and force to pounds-force
            const massLb = mass * 2.20462; // converting kg to lb
            forceConverted = ForceConverter.NtoLbf(forceN); // Convert newtons to pounds-force
            break;
    }

    // Rounding off the final value
    forceConverted = math.round(forceConverted, 3); // rounding to 3 decimal places

    // Return the structured data
    return {
        params: {
            g: n,
            mass: selectedSystem === 'si' ? mass : mass * 2.20462, // converting kg to lb if necessary
            unitsForce: units.force,
            unitsMass: units.mass,
            unitsAcceleration: units.acceleration
        },
        correct_answers: {
            F: forceConverted
        },
        nDigits: 3,
        sigfigs: 3
    };
};

module.exports = {
    generate
};

// Example usage
const result = generate();
console.log(result);
