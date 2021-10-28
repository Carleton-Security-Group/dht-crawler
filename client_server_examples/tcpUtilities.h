
////////////////////////////////////////////////////////////////
//
//	tcpUtilities.h
//
//	Adapted in C from Douglas Comer's "Internetworking
//		with TCP/IP" by Jeff Ondich and Lauren Jantz,
//		summer 1995.
//
//	Rewritten in C++, Jeff Ondich, January 2000
//
//	The functions prototyped here are used by the
//	example client (helloClient.cpp) and servers
//	(helloServer.cpp and helloConcurrent.cpp).
//
////////////////////////////////////////////////////////////////

#define		DEFAULT_QUEUE_LENGTH 	5


/////////////////////////////////////
// Client function prototypes.
/////////////////////////////////////

int MakeConnection( const char *hostName, int port );


/////////////////////////////////////
// Server function prototypes.
/////////////////////////////////////

int PrepareToAcceptConnections( int port );
int Accept( int sock );


/////////////////////////////////////
// Client and server function
// prototypes.
/////////////////////////////////////

int ReadFromSocket( int sock, char *buffer, int nBytes );
void GetPeerHostName( int sock, char *name, int nameArrayLimit );
