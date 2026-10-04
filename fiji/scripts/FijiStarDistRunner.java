/**
 * Headless, reproducible runner for the published ImageJ/Fiji StarDist 2D command.
 *
 * <p>Usage: {@code FijiStarDistRunner input.tif label-output.tif [nTiles]}. The
 * StarDist 0.3.0-scijava bundled fluorescent-nuclei model is used with its
 * optimized thresholds: probability/score=0.479071 and overlap-NMS=0.3.</p>
 */

import java.util.HashMap;
import java.util.Map;

import de.csbdresden.stardist.StarDist2D;
import net.imagej.Dataset;
import net.imagej.ImageJ;
import org.scijava.command.CommandModule;

public final class FijiStarDistRunner {
    private FijiStarDistRunner() {}

    public static void main(final String... args) throws Exception {
        if (args.length < 2 || args.length > 3) {
            throw new IllegalArgumentException(
                "Usage: FijiStarDistRunner input.tif label-output.tif [nTiles]"
            );
        }

        final int nTiles = args.length == 3 ? Integer.parseInt(args[2]) : 1;
        if (nTiles < 1) throw new IllegalArgumentException("nTiles must be >= 1");

        final ImageJ ij = new ImageJ();
        final Map<String, Object> parameters = new HashMap<>();
        parameters.put("input", (Dataset) ij.io().open(args[0]));
        parameters.put("modelChoice", "Versatile (fluorescent nuclei)");
        parameters.put("normalizeInput", true);
        parameters.put("percentileBottom", 1.0);
        parameters.put("percentileTop", 99.8);
        parameters.put("probThresh", 0.479071);
        parameters.put("nmsThresh", 0.3);
        parameters.put("outputType", "Label Image");
        parameters.put("nTiles", nTiles);
        parameters.put("excludeBoundary", 2);
        parameters.put("roiPosition", "Automatic");
        parameters.put("verbose", false);
        parameters.put("showCsbdeepProgress", false);
        parameters.put("showProbAndDist", false);

        try {
            final long startNanos = System.nanoTime();
            final CommandModule module = ij.command().run(StarDist2D.class, false, parameters).get();
            final double elapsedSeconds = (System.nanoTime() - startNanos) / 1_000_000_000.0;
            final Dataset label = (Dataset) module.getOutput("label");
            if (label == null) throw new IllegalStateException("StarDist produced no Label Image output.");
            ij.io().save(label, args[1]);

            System.out.printf("INPUT=%s%nOUTPUT=%s%nMODEL=Versatile (fluorescent nuclei)%n" +
                "PROB_THRESH=0.479071%nNMS_THRESH=0.3%nNTILES=%d%nRUNTIME_S=%.6f%n",
                args[0], args[1], nTiles, elapsedSeconds);
        } finally {
            ij.context().dispose();
        }
        System.exit(0);
    }
}
