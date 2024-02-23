/**
 * Importing Data from "math_helpers" File
 * 
 * Usage:
 * const mathUtils = require('./math_helpers');
 * 
 * Description:
 * This module demonstrates how to import data from a file named "mathhelpers"
 * using the `require` statement in JavaScript. Make sure the file is in the same
 * directory as your script or provide the correct path to the file.
 */

const math = require('mathjs');

/**
 * const{removeItemOnce} = require('./math_helpers');
 * Removes the first occurrence of a value from an array, if it exists.
 * @param {Array} arr - The array from which to remove the value.
 * @param {*} value - The value to remove from the array.
 * @returns {Array} The array with the value removed, if found.
 */
function removeItemOnce(arr, value) {
    var index = arr.indexOf(value);
    if (index > -1) {
      arr.splice(index, 1);
    }
    return arr;
}

/**
 * * Usage:
 * const{getRandomPermutationArray} = require('./math_helpers');
 * Generates a random permutation of an array.
 * @param {math.Matrix} A1 - A mathjs Matrix object containing the original array.
 * @returns {Array} A new array containing the elements of the original array in random order.
 */
function getRandomPermutationArray(A1) {
    A = A1._data;
    numEls = A.length;
    B = [];
    for (let i = 0; i < numEls; i++) {
        x = math.pickRandom(A);
        y = removeItemOnce(A, x);
        B.push(x);
    }
    return B;
}

/**
 * const{getRandomPermutationRange} = require('./math_helpers');
 * Generates a random permutation of numbers from 0 to a specified number.
 * @param {number} num - The upper limit of the range (exclusive).
 * @returns {Array} An array containing a random permutation of numbers from 0 to num-1.
 */
function getRandomPermutationRange(num) {
    A = math.range(0, num);
    B = getRandomPermutationArray(A);
    return B;
}

/**const{getRandomInt} = require('./math_helpers');
 * Returns a random integer between 0 and a specified value.
 * @param {number} max - The upper limit for the random number (exclusive).
 * @returns {number} A random integer between 0 and max-1.
 */
function getRandomInt(max) {
  return Math.floor(Math.random() * max);
}

/**const{shuffleArray} = require('./math_helpers');
 * Shuffles the elements of an array in place.
 * @param {Array} array - The array to shuffle.
 */
function shuffleArray(array) {
  for (var i = array.length - 1; i > 0; i--) {
      var j = Math.floor(Math.random() * (i + 1));
      var temp = array[i];
      array[i] = array[j];
      array[j] = temp;
  }
}

/**const{getRandomMask} = require('./math_helpers');
 * Generates a random selection mask array with a specified number of ones.
 * @param {number} maxElements - The length of the mask array.
 * @param {number} minOnes - The minimum number of ones in the mask.
 * @param {number} maxOnes - The maximum number of ones in the mask.
 * @returns {Array} An array of 0s and 1s of length maxElements, with a random number of 1s between minOnes and maxOnes.
 */
function getRandomMask(maxElements, minOnes, maxOnes) {
  let selectionMask;
  (selectionMask = []).length = maxElements;
  selectionMask.fill(0);
  let numOnes = math.randomInt(minOnes, maxOnes);
  for (let i = 0; i < numOnes; i++) {
      selectionMask[i] = 1;
  }
  shuffleArray(selectionMask);
  console.log('Shuffled array = ', selectionMask);

  return selectionMask;
}

module.exports = {
    getRandomPermutationRange,
    getRandomInt,
    getRandomPermutationArray,
    shuffleArray,
    getRandomMask
};
