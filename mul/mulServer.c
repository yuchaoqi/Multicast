/*下面是一个多播服务器的例子。多播服务器的程序设计很简单，建立一个数据包套接字，选定多播的IP地址和端口，直接向此多播地址发送数据就可以了。
多播服务器的程序设计，不需要服务器加入多播组，可以直接向某个多播组发送数据。
*/
/*
*broadcast_server.c - 多播服务程序
*/
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <errno.h>
#include <strings.h>

#define MCAST_PORT    8888
#define MCAST_ADDR    "224.0.0.88" /*一个局部连接多播地址，路由器不进行转发*/
#define MCAST_DATA    "Linux c multicast data" /*多播发送的数据*/
#define MCAST_INTERVAL    5 /*发送间隔时间*/
int main(int argc, char*argv)
{
	int s;
	struct sockaddr_in    my_mcast_addr;
	s = socket(AF_INET,    SOCK_DGRAM, 0); /*建立套接字*/
	if (s == -1)
	{
		perror("socket()");
		return -1;
	}
	memset(&my_mcast_addr, 0, sizeof(my_mcast_addr));/*初始化IP多播地址为0*/
	my_mcast_addr.sin_family = AF_INET;/*设置协议族类行为AF*/
	my_mcast_addr.sin_addr.s_addr = inet_addr(MCAST_ADDR);/*设置多播IP地址*/
	my_mcast_addr.sin_port = htons(MCAST_PORT);/*设置多播端口*/
	
	/*向多播地址发送数据*/
	/*发送一次数据*/
	int n = sendto(s, /*套接字描述符*/
				MCAST_DATA, /*数据*/
				sizeof(MCAST_DATA), /*长度*/
				0,(struct sockaddr*)&my_mcast_addr, sizeof(my_mcast_addr)) ;
	if( n < 0)
	{
		perror("sendto()");
		return -2;
	}
	/*
	//持续向多播IP地址"224.0.0.88"的8888端口发送数据"BROADCAST TEST DATA"，每发送一次间隔5s。
	while(1) {
		int n = sendto(s, //套接字描述符
				MCAST_DATA, //数据
				sizeof(MCAST_DATA), //长度
				0,(struct sockaddr*)&my_mcast_addr, sizeof(my_mcast_addr)) ;
		if( n < 0)
		{
			perror("sendto()");
			return -2;
		}
		sleep(MCAST_INTERVAL);    //等待一段时间
	}
	*/
	return 0;
}