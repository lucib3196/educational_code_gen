const math = require('mathjs');

class SpeedConverter {
    static ftstoMPH(speedFts) {
        return speedFts * (3600 / 5280);
    }

    static mstoKmH(speedMs) {
        return speedMs * (3600 / 1000);
    }

    static mphToFts(speedMPH) {
        return speedMPH * (5280 / 3600);
    }

    static kmHtoMs(speedKMH) {
        return speedKMH * (1000 / 3600);
    }
}

const generate = () => {
    const unitSystems = {
        si: {
            speed: 'km/h',
            distance: 'm',
            time: 's',
            acceleration: 'm/s^2'
        },
        uscs: {
            speed: 'mph',
            distance: 'ft',
            time: 's',
            acceleration: 'ft/s^2'
        }
    };

    const selectedSystem = math.randomInt(0, 2) === 0 ? 'si' : 'uscs';
    const units = unitSystems[selectedSystem];

    const v0 = math.randomInt(10, 31);
    const a = math.randomInt(1, 11);
    const t = math.randomInt(1, 11);

    let v0_converted, vf_converted;

    switch (selectedSystem) {
        case "si":
            v0_converted = SpeedConverter.kmHtoMs(v0);
            break;
        case "uscs":
            v0_converted = SpeedConverter.mphToFts(v0);
            break;
    }

    let vf = v0_converted + a * t;

    switch (selectedSystem) {
        case "si":
            vf_converted = SpeedConverter.mstoKmH(vf);
            break;
        case "uscs":
            vf_converted = SpeedConverter.ftstoMPH(vf);
            break;
    }

    vf_converted = math.round(vf_converted, 3);

    return {
        params: {
            v: v0,
            a: a,
            t: t,
            unitsSpeed: units.speed,
            unitsTime: units.time,
            unitsAcceleration: units.acceleration
        },
        correct_answers: {
            v: vf_converted
        },
        nDigits: 3,
        sigfigs: 3
    };
};

module.exports = {
    generate
};