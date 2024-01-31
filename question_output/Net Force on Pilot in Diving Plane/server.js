const math = require('mathjs');

/**
 * The ForceConverter class provides static methods to convert forces between
 * different units: Newtons (N), pounds-force (lbf).
 */
class ForceConverter {
    /**
     * Converts force from Newtons to pounds-force.
     * 
     * @param {number} forceN - The force in Newtons.
     * @return {number} The force in pounds-force.
     */
    static NtoLbf(forceN) {
        return forceN / 4.44822;
    }

    /**
     * Converts force from pounds-force to Newtons.
     * 
     * @param {number} forceLbf - The force in pounds-force.
     * @return {number} The force in Newtons.
     */
    static LbftoN(forceLbf) {
        return forceLbf * 4.44822;
    }
}

const generate = () => {
    const unitSystems = {
        si: {
            force: 'N',
            mass: 'kg',
            acceleration: 'm/s^2',
            gravitationalAcceleration: 9.81 // m/s^2
        },
        uscs: {
            force: 'lbf',
            mass: 'lb',
            acceleration: 'ft/s^2',
            gravitationalAcceleration: 32.174 // ft/s^2
        }
    };

    // Dynamic Parameter Selection
    const selectedSystem = math.randomInt(0, 2) === 0 ? 'si' : 'uscs';
    const units = unitSystems[selectedSystem];

    // Value Generation
    const a = math.randomInt(2, 10); // Acceleration in terms of g
    const mass = selectedSystem === 'si' ? math.randomInt(60, 100) : math.randomInt(132, 220); // Mass in kg or lb

    // Calculating Net Force
    let netForce;
    if (selectedSystem === 'si') {
        netForce = mass * a * units.gravitationalAcceleration; // F = ma (in Newtons)
    } else {
        // Convert mass to kg for calculation, then convert force back to lbf
        const massInKg = mass / 2.20462; // Convert lb to kg
        netForce = ForceConverter.LbftoN(massInKg * a * 9.81); // F = ma in N, then convert to lbf
    }

    // Rounding off the final value
    netForce = math.round(netForce, 3); // rounding to 3 decimal places

    // Return the structured data
    return {
        params: {
            a: a,
            mass: mass,
            unitsForce: units.force,
            unitsMass: units.mass,
            unitsAcceleration: units.acceleration
        },
        correct_answers: {
            F: netForce
        },
        nDigits: 3,
        sigfigs: 3
    };
};

module.exports = {
    generate,
    ForceConverter
};

// Example usage:
const result = generate();
console.log(result);