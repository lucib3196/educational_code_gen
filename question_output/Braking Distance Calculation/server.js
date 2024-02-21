const math = require('mathjs');

function convertMPHtoFts(speedMPH) {
    const conversionFactor = 1.46667; // This factor converts mph to ft/s
    return speedMPH * conversionFactor;
}

function convertKmphToMs(speedKmph) {
    const conversionFactor = 0.277778; // This factor converts km/h to m/s
    return speedKmph * conversionFactor;
}

const generate = () => {
    const unitSystems = {
        si: {
            speed: 'km/h',
            acceleration: 'm/s²',
            distance: 'm',
            time: 's'
        },
        uscs: {
            speed: 'mph',
            acceleration: 'ft/s²',
            distance: 'ft',
            time: 's'
        }
    };

    // 1. Dynamic Parameter Selection
    const selectedSystem = math.randomInt(0, 2) === 0 ? 'si' : 'uscs';
    const units = unitSystems[selectedSystem];

    // 3. Value Generation
    const v1 = math.randomInt(30, 101); // initial velocity between 30 and 100 units
    const d1 = math.randomInt(50, 201); // braking distance between 50 and 200 units
    const t1 = math.randomInt(1, 11); // time between 1 and 10 seconds

    // Conversion based on unit system
    let v1_converted;
    if (units.speed === "km/h") {
        v1_converted = convertKmphToMs(v1);
    } else if (units.speed === "mph") {
        v1_converted = convertMPHtoFts(v1);
    }

    // 4. Solution Synthesis
    // Assuming constant deceleration, we use the formula: d = v * t - (1/2) * a * t^2
    // However, we need to find 'a' from the given braking distance (d1) and initial speed (v1)
    // v^2 = u^2 + 2as => a = (v^2 - u^2) / (2s)
    let a = -(Math.pow(v1_converted, 2)) / (2 * d1); // Deceleration
    let d = v1_converted * t1 + (1/2) * a * Math.pow(t1, 2); // Distance traveled in t1 seconds

    // Return the structured data
    return {
        params: {
            v1: v1,
            d1: d1,
            t1: t1,
            unitsSpeed: units.speed,
            unitsAcceleration: units.acceleration,
            unitsDist: units.distance,
            unitsTime: units.time
        },
        correct_answers: {
            d: math.round(d,3) // Round to 3 decimal places
        },
        nDigits: 3,
        sigfigs: 3
    };
};

module.exports = {
    generate
};