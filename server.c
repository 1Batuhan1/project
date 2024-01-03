#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <netinet/in.h>

#define Port xxxx

bind(serverSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress));

//Listening part for connection.
listen(serverSocket, 5);

//Accept the connection.
int clientSocket = accept(serverSocket, NULL, NULL);

void handle_retr(int data_socket, const char *filename) {
    FILE *file = fopen(filename, "rb");
    if (file == NULL) {
        // Handle file not found
        send(data_socket, "File not found\r\n", strlen("File not found\r\n"), 0);
        close(data_socket);
        return;
    }

    send(data_socket, "Opening data connection\r\n", strlen(" Opening data connection\r\n"), 0);

    // Read and send the file data
    char buffer[1024];
    size_t bytesRead;
    while ((bytesRead = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        send(data_socket, buffer, bytesRead, 0);
    }

    fclose(file);
    send(data_socket, "226 Transfer complete\r\n", strlen("226 Transfer complete\r\n"), 0);
    close(data_socket);
}

int main() {
    //creation of the socket
    int serverSocket = socket(AF_INET, SOCK_STREAM, 0);

//Binding the Socket.
    struct sockaddr_in serverAddress;
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_addr.s_addr = INADDR_ANY;
    serverAddress.sin_port = htons(21);

    bind(serverSocket, (struct sockaddr*)&serverAddress, sizeof(serverAddress));
    listen(serverSocket, 5);


    //accept client connection
    while (1) {
        int clientSocket = accept(serverSocket, NULL, NULL);


        const char *filename = "example.txt"; //  you should  Replace with actual filename

        // Set up a separate socket for data connection
        int dataSocket = socket(AF_INET, SOCK_STREAM, 0);
        struct sockaddr_in dataAddress;
        dataAddress.sin_family = AF_INET;
        dataAddress.sin_addr.s_addr = INADDR_ANY;
        dataAddress.sin_port = htons(DATA_PORT);

        bind(dataSocket, (struct sockaddr*)&dataAddress, sizeof(dataAddress));
        listen(dataSocket, 1);

        // Inform the client about the data connection details
        char dataConnectionMsg[50];
        sprintf(dataConnectionMsg, "227 Entering Passive Mode (127,0,0,1,%d,%d)\r\n", DATA_PORT / 256, DATA_PORT % 256);
        send(clientSocket, dataConnectionMsg, strlen(dataConnectionMsg), 0);

        // Accept the data connection from the client
        int dataClientSocket = accept(dataSocket, NULL, NULL);

        // Handle the retr command and data transfer
        handle_retr(dataClientSocket, filename);

        close(clientSocket);
    }

    close(serverSocket);
    return 0;
}