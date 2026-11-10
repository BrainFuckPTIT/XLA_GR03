import ij.IJ;
import ij.ImagePlus;
import ij.process.ByteProcessor;
import ij.process.ImageProcessor;

/** Measure foreground Dice through ImageJ's image and histogram APIs. */
public class MeasureDice {
    public static void main(String[] args) {
        if (args.length != 2) throw new IllegalArgumentException("Expected GT and prediction TIFF paths");
        ImagePlus gt = IJ.openImage(args[0]);
        ImagePlus pred = IJ.openImage(args[1]);
        if (gt == null || pred == null || gt.getStackSize() != 1 || pred.getStackSize() != 1 ||
                gt.getWidth() != pred.getWidth() || gt.getHeight() != pred.getHeight())
            throw new IllegalArgumentException("Images must be readable 2D TIFFs of equal size");
        ImageProcessor a = gt.getProcessor(), b = pred.getProcessor();
        ByteProcessor ma = new ByteProcessor(gt.getWidth(), gt.getHeight());
        ByteProcessor mb = new ByteProcessor(gt.getWidth(), gt.getHeight());
        ByteProcessor both = new ByteProcessor(gt.getWidth(), gt.getHeight());
        for (int i = 0; i < gt.getWidth() * gt.getHeight(); i++) {
            boolean x = a.getf(i) > 0, y = b.getf(i) > 0;
            ma.set(i, x ? 255 : 0); mb.set(i, y ? 255 : 0); both.set(i, x && y ? 255 : 0);
        }
        int na = ma.getHistogram()[255], nb = mb.getHistogram()[255], ni = both.getHistogram()[255];
        double dice = na + nb == 0 ? 0.0 : 2.0 * ni / (na + nb);
        System.out.printf(java.util.Locale.ROOT, "%d,%d,%d,%.12f%n", na, nb, ni, dice);
    }
}
