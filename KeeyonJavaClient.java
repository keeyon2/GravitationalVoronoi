import java.util.Random;
import java.util.StringTokenizer;
import java.awt.Point;
import java.util.ArrayList;
import java.io.PrintWriter;
import java.io.Writer;
import java.io.BufferedWriter;
import java.io.OutputStreamWriter;
import java.io.FileOutputStream;

/**
 * Created by ylc265 on 10/24/15.
 */
public class KeeyonJavaClient extends VoronoiClient{
    Random rand = new Random();
    int[][] grid;
    ArrayList<Point> myPoints;
    ArrayList<Point> theirPoints;
    Writer writer;
   
    
    KeeyonJavaClient(String server, int port, String username, int n) {
        super(server, port, username);
        /*
        File myFile = new File(username); 
        FileUtils.writeStringToFile(myFile, "HII", "WOrking?");
        */
        try {
            writer = new BufferedWriter(new OutputStreamWriter(
                new FileOutputStream(username+".txt"), "utf-8"));           
        }
        catch (Exception ignoreException) {

        }
        writer.write("Something to write to writer");
        grid = new int[n][n];
    }

    // random strategy
    @Override
    public String process(String command) throws Exception {
        if (command.equals("TEAM")) {
            writer.write("PRINTS ARE WORKING");
            return super.username;
        }

        if (command.matches("[A-Za-z0-9-_]+ \\d+ \\d+")) {
            StringTokenizer tk2 = new StringTokenizer(command, " ");
            // Use this in your code if necessary, skipping here
            String player_name = tk2.nextToken();
            int px = Integer.parseInt(tk2.nextToken());
            int py = Integer.parseInt(tk2.nextToken());
            writer.write("I have received " + px + "and " + py);
            grid[px][py] = 2;
            
            Point theirPoint = new Point(px, py);
            theirPoints.add(theirPoint);
        }

        if (command.equals("MOVE")) {
            int myx, myy;
            
            // MAKE MY MOVE
            
            // if first move
            if (theirPoints.isEmpty() && myPoints.isEmpty()) {
                myx = 499;
                myy = 499;
                UpdateBoardWithMyMove(499, 499);
                writer.write("WE ARE EMPTY!");
                writer.write("WE ARE EMPTY!");
                writer.write("WE ARE EMPTY!");
                writer.write("WE ARE EMPTY!");
                writer.write("WE ARE EMPTY!");
                return String.format("%d %d", myx, myy);
            }
            
            // Rest
            do {
                myx = rand.nextInt(grid.length);
                myy = rand.nextInt(grid.length);
            } while (grid[myx][myy] != 0);

            UpdateBoardWithMyMove(myx, myy);
            return String.format("%d %d", myx, myy);
        }

        if (command.equals("RESTART")) {
            for (int i=0; i<grid.length; i++) {
                for (int j=0; j<grid.length; j++) {
                    grid[i][j] = 0;
                }
            }
        }

        if (command.equals("END")) {
            writer.close();
            System.exit(0);
        }

        return "";
    }

    public void UpdateBoardWithMyMove(int x, int y) {
        grid[x][y] = 1;
        Point myNextPoint = new Point(x, y);
        myPoints.add(myNextPoint); 
    }

    public static void main(String[] args) {
        int port;
        String name = "";
        if (args.length < 1) {
            System.out.println("Need atleast the name.");
            System.exit(0);
        } else {
            name = args[0];
        }
        if (args.length == 2) {
            port = Integer.parseInt(args[1]);
        } else {
            port = 1337;
        }
        System.out.format("My name is %s\n", name);
        JavaClient client = new JavaClient("localhost", port, name, 1000);
        client.start();
