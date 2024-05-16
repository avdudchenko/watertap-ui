const { defineConfig } = require("cypress");

module.exports = defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // implement node event listeners here
      
    },
    baseUrl: process.env.REACT_APP_FRONTEND_SERVER,
    video: true
  },
});
