const path = require('path');
module.exports = {
  output: {
    filename: 'main.js',
  },
  mode: 'production',
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader']
      }
    ]
  },
};
