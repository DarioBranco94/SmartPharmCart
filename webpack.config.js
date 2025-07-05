const path = require('path');

module.exports = {
    entry: './src/index.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'public')
    },
    mode: 'development',
    experiments: {
        topLevelAwait: true
    },
    module: {
        rules: [
            {
                test: /\.glb$/,
                type: 'asset/resource'
            }
        ]
    }
};
