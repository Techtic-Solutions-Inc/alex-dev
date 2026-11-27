/** @type {import('jest').Config} */
module.exports = {
  projects: [
    {
      displayName: 'unit',
      moduleFileExtensions: ['js', 'json', 'ts'],
      rootDir: 'src',
      testRegex: '.*\\.spec\\.ts$',
      testPathIgnorePatterns: ['/node_modules/', '/dist/'],
      setupFiles: ['<rootDir>/../test/jest-common-setup.ts'],
      transform: {
        '^.+\\.(t|j)s$': 'ts-jest',
      },
      collectCoverageFrom: ['**/*.(t|j)s'],
      coverageDirectory: '../coverage',
      testEnvironment: 'node',
    },
    {
      displayName: 'e2e',
      moduleFileExtensions: ['js', 'json', 'ts'],
      rootDir: '.',
      testRegex: '.*\\.e2e-spec\\.ts$',
      globalSetup: '<rootDir>/test/global-setup.ts',
      globalTeardown: '<rootDir>/test/global-teardown.ts',
      setupFiles: [
        '<rootDir>/test/jest-common-setup.ts',
        '<rootDir>/test/setup-env-after-global.ts',
        '<rootDir>/test/setup-env.ts',
      ],
      testPathIgnorePatterns: ['/node_modules/', '/dist/'],
      transform: {
        '^.+\\.(t|j)s$': 'ts-jest',
      },
      testEnvironment: 'node',
    },
  ],
};
