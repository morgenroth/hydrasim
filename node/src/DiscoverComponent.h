/*
 * DiscoverComponent.h
 *
 *  Created on: 14.01.2011
 *      Author: morgenro
 */

#ifndef DISCOVERCOMPONENT_H_
#define DISCOVERCOMPONENT_H_

#include <ibrcommon/net/MulticastSocket.h>
#include <ibrcommon/net/vsocket.h>
#include <ibrcommon/net/vaddress.h>
#include <iostream>

class DiscoverComponent
{
public:
	DiscoverComponent(const std::string &hostname, unsigned int port = 3232);
	virtual ~DiscoverComponent();

	void run();

private:
	class Message
	{
	public:
		enum MSG_TYPE
		{
			MSG_HELLO = 0,
			MSG_NODE = 1
		} _type;

		Message(const MSG_TYPE type = MSG_HELLO);
		virtual ~Message();

		std::string _hostname;
	};

	friend
	std::ostream& operator<<(std::ostream&, const Message &msg);

	friend
	std::istream& operator>>(std::istream&, Message &msg);

	ibrcommon::vsocket _vsock;
	ibrcommon::vaddress _vaddress;
	ibrcommon::MulticastSocket _msock;
	const std::string _hostname;
};

#endif /* DISCOVERCOMPONENT_H_ */
