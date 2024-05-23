import * as path from "path";

import { getConfig } from "./webpack.base.config";

process.env.NODE_ENV = "development";

export default getConfig({
    mode: "development",
    output: {
        path: path.resolve("./assets/libdev/"),
        basename: "[name]-[contenthash]",
    },
    devtool: "source-map",
});
