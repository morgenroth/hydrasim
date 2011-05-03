/*
 * DiscoverComponent.cpp
 *
 *  Created on: 14.01.2011
 *      Author: morgenro
 */

#include "DiscoverComponent.h"
#include <sstream>

DiscoverComponent::Message::Message(const DiscoverComponent::Message::MSG_TYPE type)
 : _type(type), _hostname()
{
}

DiscoverComponent::Message::~Message()
{

}

std::ostream& operator<<(std::ostream &stream, const DiscoverComponent::Message &msg)
{
	stream.write((char*)&msg._type, 1);

	switch (msg._type)
	{
		case DiscoverComponent::Message::MSG_HELLO:
		{
			stream << "HELLO" << std::flush;
			break;
		}

		case DiscoverComponent::Message::MSG_NODE:
		{
			uint32_t len_of_name = htonl(msg._hostname.length());
			stream.write((char*)&len_of_name, 4);
			stream << msg._hostname;
			break;
		}
	}
}

std::istream& operator>>(std::istream &stream, DiscoverComponent::Message &msg)
{
	char type = 0;
	stream.read(&type, 1);
	msg._type = (DiscoverComponent::Message::MSG_TYPE)type;

	switch (msg._type)
	{
		case DiscoverComponent::Message::MSG_HELLO:
		{
			break;
		}

		case DiscoverComponent::Message::MSG_NODE:
		{
			break;
		}
	}
}

DiscoverComponent::DiscoverComponent(const std::string &hostname, unsigned int port)
 : _vsock(), _msock(_vsock.bind(port, SOCK_DGRAM)), _vaddress(ibrcommon::vaddress::VADDRESS_INET, "225.16.16.1"), _hostname(hostname)
{
	_msock.joinGroup(_vaddress);
}

DiscoverComponent::~DiscoverComponent()
{
	_msock.leaveGroup(_vaddress);
}

void DiscoverComponent::run()
{
	char data[1500];

	while (true)
	{
		std::list<int> fds;
		ibrcommon::select(_vsock, fds, NULL);

		for (std::list<int>::const_iterator iter = fds.begin(); iter != fds.end(); iter++)
		{
			// socket to read
			int s = (*iter);

			struct sockaddr_in clientAddress;
			socklen_t clientAddressLength = sizeof(clientAddress);

			// data waiting
			int len = recvfrom(s, data, 1500, MSG_WAITALL, (struct sockaddr *) &clientAddress, &clientAddressLength);

			std::stringstream ss; ss.write(data, len);

			Message m;
			ss >> m;

			// response to any HELLO
			if (m._type == Message::MSG_HELLO)
			{
				std::cout << "HELLO received" << std::endl;

				Message reply(Message::MSG_NODE);
				reply._hostname = _hostname;

				std::stringstream ss; ss << reply;
				std::string reply_data = ss.str();

				int ret = sendto(s, reply_data.c_str(), reply_data.length(), 0, (struct sockaddr *) &clientAddress, clientAddressLength);
			}
		}
	}
}
