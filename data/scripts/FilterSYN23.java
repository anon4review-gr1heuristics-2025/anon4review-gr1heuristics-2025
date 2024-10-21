package tau.smlab.syntech.royrun.syn23filter;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.stream.Stream;
// Taken from Dor code. used to extract the specs

public class FilterSYN23 {
    public static final String INPUT_PATH = "./UNFILTERED/original";
    public static final String OUTPUT_PATH = "./FILTERED111";
    public static int i = 0;

    public static void main(String[] args) {
        try {
            processFolder(INPUT_PATH, OUTPUT_PATH);
        } catch (IOException e) {
            System.err.println("Error processing files: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void processFolder(String inputPath, String outputPath) throws IOException {
        Path inputDir = Paths.get(inputPath);
        Path outputDir = Paths.get(outputPath);

        Files.createDirectories(outputDir);

        try (Stream<Path> paths = Files.walk(inputDir)) {
            paths
            .filter(path -> !containsFrogInPath(path))
                 .filter(Files::isRegularFile)
                 .filter(path -> path.toString().endsWith(".spectraArxived"))
                 .forEach(path -> copyFile(path, inputDir, outputDir));
        }
    }

    private static boolean containsFrogInPath(Path path) {
        return path.toString().toLowerCase().contains("frog");
    }

    private static void copyFile(Path file, Path inputDir, Path outputDir) {
        try {
            Path relativePath = inputDir.relativize(file);
            String filename = relativePath.getFileName().toString();

            // Change the file extension to '.spectra'
            String newFilename = filename.replace(".spectraArxived", ".spectra");

            // Reconstruct the relative path with the new filename
            Path parentDir = relativePath.getParent();
            if (parentDir != null) {
                relativePath = parentDir.resolve(newFilename);
            } else {
                relativePath = Paths.get(newFilename);
            }

            Path destination = outputDir.resolve(relativePath);
            Files.createDirectories(destination.getParent());
            Files.copy(file, destination, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("Copied and renamed: " + relativePath);
        } catch (IOException e) {
            System.err.println("Failed to copy and rename file: " + file);
            e.printStackTrace();
        }
    }
}
