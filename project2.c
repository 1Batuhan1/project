#include<fstream>
#include<stdio.h>
#include<iostream>
using namespace std;  

//defining the LL elements.
struct node
{
    int data;
    struct node *next ;
};
struct node * createNode(int data);
struct node * insertfront (struct node *header,int data);
void display(struct node *);
int main()
{
  
    //read inputs from file.
    FILE* file=fopen("inputs.txt","rb");
int n[6];
fscanf(file,"%d%d%d%d%d%d",&n[0],&n[1],&n[2],&n[3],&n[4],&n[5]);
 
 /* int a,b;    
a = n[1]; 
b = n[2];
cout <<a+b<<endl;
*/

/*struct node *header = NULL;
header = (struct node *) malloc(sizeof(node));
header->data = n[0];
header->next = NULL;

cout<< header->data<<endl;;
cout << header->next;
*/
struct node *header = NULL;
header = createNode(0);
header = insertfront(header,n[0]);
header = insertfront(header,n[1]);
header = insertfront(header,n[2]);
header = insertfront(header,n[3]);
display(header);
cout<<endl;


getchar();
return 0;
 }
 //Display part of the LL.
 void display(struct node *header)
 {
     struct node *temp = header;
     while (temp != NULL)
     {
         
         cout << temp->data <<"-->";
         temp = temp->next;
        
     }
     
     cout<<endl;
}
//Create new node.
struct node *createNode(int item)
{
    
    struct node * temp;
    temp = (struct node *) malloc(sizeof(node));
    temp->data = item;
    temp->next = NULL;
    return temp;
}
//Adding a data.
  struct node * insertfront (struct node *header,int data)
 {
     //create a node.
     struct node * temp = createNode (data);
     //connection of the new node to the front of the list.
     temp->next = header;
     
     header=temp;
     return header;
     
 }
     
 
 
 
 
 
 
 
 
 
 
 
