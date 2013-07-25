/*多播组的IP地址为224.0.0.88，端口为8888，当客户端接收到多播的数据后将打印 出来。
客户端只有在加入多播组后才能接受多播组的数据，因此多播客户端在接收多播组的数据之前需要先加入多播组，当接收完毕后要退出多播组。
*/
/*
*broadcast_client.c - 多播的客户端
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
#define MCAST_INTERVAL    5 /*发送间隔时间*/
#define BUFF_SIZE 256 /*接收缓冲区大小*/
int main(int argc, char*argv[])
{
	int s; /*套接字文件描述符*/
	struct sockaddr_in    local_addr; /*本地地址*/
	int err = -1;
	s = socket(AF_INET,    SOCK_DGRAM, 0); /*建立套接字*/
	if (s == -1)
	{
	perror("socket()");
	return -1;
	}
	/*初始化地址*/
	memset(&local_addr,    0, sizeof(local_addr));
	local_addr.sin_family =    AF_INET;
	local_addr.sin_addr.s_addr    = htonl(INADDR_ANY);
	local_addr.sin_port =    htons(MCAST_PORT);
	/*绑定socket*/
	err = bind(s,(struct    sockaddr*)&local_addr, sizeof(local_addr))    ;
	if(err < 0)
	{
	perror("bind()");
	return -2;
	}
	/*设置回环许可*/
	int loop = 1;
	err =    setsockopt(s,IPPROTO_IP, IP_MULTICAST_LOOP,&loop, sizeof(loop));
	if(err < 0)
	{
	perror("setsockopt():IP_MULTICAST_LOOP");
	return -3;
	}
	struct ip_mreq mreq; /*加入广播组*/
	mreq.imr_multiaddr.s_addr    = inet_addr(MCAST_ADDR); /*广播地址*/
	mreq.imr_interface.s_addr    = htonl(INADDR_ANY); /*网络接口为默认*/
	/*将本机加入广播组*/
	err = setsockopt(s,    IPPROTO_IP, IP_ADD_MEMBERSHIP,&mreq, sizeof
		(mreq));
	if (err < 0)
	{
	perror("setsockopt():IP_ADD_MEMBERSHIP");
	return -4;
	}

	int addr_len = 0;
	char buff[BUFF_SIZE];
	int n = 0;
	// 接收消息一次
	addr_len =    sizeof(local_addr);
	memset(buff, 0,    BUFF_SIZE); //清空接收缓冲区
	//接收数据
	n = recvfrom(s, buff,    BUFF_SIZE, 0,(struct sockaddr*)&local_addr,&addr_len);
	if( n== -1)
	{
		perror("recvfrom()");
	}
	//打印信息
	printf("Received message from server:%s\n", buff);
	
	/*
	//循环接收广播组的消息，5次后退出
	int times = 0;
	for(times =    0;times<5;times++)
	{
		addr_len =    sizeof(local_addr);
		memset(buff, 0,    BUFF_SIZE); //清空接收缓冲区
		//接收数据
		n = recvfrom(s, buff,    BUFF_SIZE, 0,(struct sockaddr*)&local_addr,&addr_len);
		if( n== -1)
		{
			perror("recvfrom()");
		}
		//打印信息
		printf("Recv %dst    message from server:%s\n", times, buff);
		sleep(MCAST_INTERVAL);
	}
	*/
	/*退出广播组*/
	err = setsockopt(s,    IPPROTO_IP, IP_DROP_MEMBERSHIP,&mreq, sizeof(mreq));
	close(s);
	return 0;
}