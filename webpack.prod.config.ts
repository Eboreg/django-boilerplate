import * as path from "path";

import { getConfig } from "./webpack.base.config";

process.env.NODE_ENV = "production";

export default getConfig({
    mode: "production",
    output: {
        path: path.resolve("./assets/lib/"),
        basename: "[name]-[contenthash]",
    },
});
