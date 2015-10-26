import java.util.Random;
import java.util.StringTokenizer;

/**
 * Created by ylc265 on 10/24/15.
 */
public class JavaClient extends VoronoiClient{
    Random rand = new Random();
    int[][] grid;
    JavaClient(String server, int port, String username, int n) {
        super(server, port, username);
        grid = new int[n][n];
    }

    // random strategy
    @Override
    public String process(String command) {
        if (command.equals("TEAM")) {
            return super.username;
        }

        if (command.matches("[A-Za-z0-9-_]+ \\d+ \\d+")) {
            StringTokenizer tk2 = new StringTokenizer(command, " ");
            // Use this in your code if necessary, skipping here
            String player_name = tk2.nextToken();
            int px = Integer.parseInt(tk2.nextToken());
            int py = Integer.parseInt(tk2.nextToken());
            grid[px][py] = 1;
        }

        if (command.equals("MOVE")) {
            int myx, myy;
            do {
                myx = rand.nextInt(grid.length);
                myy = rand.nextInt(grid.length);
            } while (grid[myx][myy] != 0);
            grid[myx][myy] = 1;
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
            System.exit(0);
        }

        return "";
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
    }
}
