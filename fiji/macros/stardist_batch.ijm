// StarDist 2D batch protocol for Fiji/ImageJ.
//
// Before first use: Help > Update... > Manage update sites > enable "CSBDeep",
// "StarDist", and "TensorFlow", apply changes, then restart Fiji. Record one interactive StarDist run with
// Plugins > Macros > Record to verify option names against the installed plugin
// version. This macro deliberately stops before the StarDist dialog so that the
// operator can select the exact model and export labels/ROIs reproducibly.

macro "StarDist batch protocol" {
    root = getDirectory("Choose folder that contains input images");
    if (root == "") exit("No input folder selected.");
    out = getDirectory("Choose folder for StarDist label images");
    if (out == "") exit("No output folder selected.");

    print("INPUT_DIR=" + root);
    print("OUTPUT_DIR=" + out);
    print("Required fixed settings: model, pmin/pmax, probability threshold, overlap threshold, nTiles.");
    list = getFileList(root);
    for (i = 0; i < list.length; i++) {
        name = list[i];
        if (endsWith(name, ".tif") || endsWith(name, ".tiff") || endsWith(name, ".png")) {
            open(root + name);
            title = getTitle();
            // Normalize and run StarDist interactively on the first image.
            // Paste the recorder-generated `run("StarDist 2D", "...")` line here
            // after checking it for your StarDist/Fiji version. Keeping it explicit
            // prevents silently changing model defaults across versions.
            run("StarDist 2D");
            waitForUser("Export the returned Label Image as TIFF to:\n" + out + "\nUse the same basename as " + name + ".\nThen click OK to continue.");
            close("*");
        }
    }
}
