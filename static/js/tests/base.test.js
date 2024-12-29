/**
 * @jest-environment jsdom
 */

const {
    test,
    expect
} = require("@jest/globals");

const {
    updateCopyrightNotice
} = require("../base.js");

describe("copyright notice tests", () => {
    test("updateCopyrightNotice updates the year correctly", () => {
        const yearElement = document.createElement("span");
        yearElement.id = "year";
        document.body.appendChild(yearElement);

        updateCopyrightNotice();

        const currentYear = new Date().getFullYear();

        expect(yearElement.innerHTML).toBe(currentYear.toString());
    });
});