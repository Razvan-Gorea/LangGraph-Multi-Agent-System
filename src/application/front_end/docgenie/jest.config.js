const nextJest = require('next/jest')

const createJestConfig = nextJest({
    dir: './', //Path to Next.js App Root Directory
})

const customJestConfig = {
    // Where to find our test setup file (For Jest)
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
    
    // Where to look for modules (For Jest)
    moduleDirectories: ['node_modules', '<rootDir>/'],
    
    // Setting up a DOM-like environment for testing
    testEnvironment: 'jest-environment-jsdom',
    
    // File Patterns To Test
    testMatch: ['**/__tests__/**/*.js', '**/?(*.)+(test).js'],
    
    // Which File Extensions To Process (For Jest)
    moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx'],

    collectCoverage: true,

    collectCoverageFrom: [
        '**/*.{js, jsx}',
        '!**/node_modules/**',
        '!**/vendor/**'
    ]
}

// Exporting The Configuration
module.exports = createJestConfig(customJestConfig)
