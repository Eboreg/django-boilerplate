import * as path from "path";

import { CleanWebpackPlugin } from "clean-webpack-plugin";
import * as MiniCssExtractPlugin from "mini-css-extract-plugin";
import * as dartsass from "sass";
import * as webpack from "webpack";

interface Options {
    mode?: "none" | "development" | "production";
    output: {
        path: string;
        basename: string;
    }
    devtool?: false | string;
}

export function getConfig(opts: Options): webpack.Configuration {
    return {
        mode: opts.mode,
        devtool: opts.devtool,
        context: __dirname,
        entry: {
            index: path.resolve("./assets/ts/index.ts"),
        },
        output: {
            path: opts.output.path,
            filename: `${opts.output.basename}.js`,
        },
        module: {
            rules: [
                {
                    test: /\.tsx?$/,
                    exclude: /node_modules/,
                    loader: "ts-loader",
                },
                {
                    test: /\.(sa|sc|c)ss$/,
                    use: [
                        MiniCssExtractPlugin.loader,
                        {
                            loader: "css-loader",
                            options: { importLoaders: 3 },
                        },
                        {
                            loader: "postcss-loader",
                            options: {
                                postcssOptions: {
                                    plugins: [
                                        ["postcss-import", { root: __dirname }],
                                    ],
                                },
                            },
                        },
                        "resolve-url-loader",
                        {
                            loader: "sass-loader",
                            options: {
                                implementation: dartsass,
                                // eslint-disable-next-line max-len
                                // Important according to https://github.com/bholloway/resolve-url-loader/blob/v5/packages/resolve-url-loader/README.md:
                                sourceMap: true,
                            },
                        },
                    ],
                },
            ],
        },
        plugins: [
            new CleanWebpackPlugin(),
            new MiniCssExtractPlugin({
                filename: `${opts.output.basename}.css`,
            }),
        ],
        resolve: {
            extensions: [".js", ".jsx", ".css", ".ts", ".tsx"],
        },
    };
}
