/*
 * CommandServer.cpp
 *
 *  Created on: 14.01.2011
 *      Author: morgenro
 */

#include "CommandServer.h"
#include "HostControl.h"
#include "FakeGPS.h"
#include <ibrcommon/net/tcpstream.h>
#include <ibrcommon/thread/MutexLock.h>


CommandServer::Connection::Connection(ibrcommon::tcpstream *stream, ibrcommon::Conditional &m, unsigned int &c)
 : _stream(stream), _active_connections_cond(m), _active_connections(c)
{
	ibrcommon::MutexLock l(_active_connections_cond);
	_active_connections++;
	_active_connections_cond.signal(true);
}

CommandServer::Connection::~Connection()
{
	delete _stream;

	ibrcommon::MutexLock l(_active_connections_cond);
	_active_connections--;
	_active_connections_cond.signal(true);
}

void CommandServer::Connection::setup()
{
	std::cout << "connection up" << std::endl;
}

void CommandServer::Connection::run()
{
	_stream->exceptions(std::ios::badbit | std::ios::eofbit);

	while (_stream->good())
	{
		Message m;

		// read a new message
		(*_stream) >> m;

		// received a new message
		std::cout << "received new message " << m._type << std::endl;

		// execute received command
		switch (m._type)
		{
			case Message::MSG_GPS_POSITION:
			{
				FakeGPS::getInstance().setPosition(m._float_values[0],
						m._float_values[1], m._float_values[2]);
				break;
			}

			case Message::MSG_SCRIPT:
			{
				HostControl::getInstance().system(m._data.str());
				break;
			}

			case Message::MSG_SHUTDOWN:
				HostControl::getInstance().shutdown();
				return;

			default:
				break;
		}
	}
}

void CommandServer::Connection::finally()
{
	_stream->close();
	std::cout << "connection down" << std::endl;
}

CommandServer::Message::Message(const CommandServer::Message::MSG_TYPE type)
 : _type(type)
{
	_float_values[0] = 0.0;
	_float_values[1] = 0.0;
	_float_values[2] = 0.0;
}

CommandServer::Message::~Message()
{
}

std::ostream& operator<<(std::ostream &stream, const CommandServer::Message &msg)
{
	stream.write((char*)&msg._type, 1);

	switch (msg._type)
	{
		default:
			break;
	}
}

std::istream& operator>>(std::istream &stream, CommandServer::Message &msg)
{
	char type = 0;
	stream.read(&type, 1);
	msg._type = (CommandServer::Message::MSG_TYPE)type;
	msg._data.str("");
	msg._float_values[0] = 0.0;
	msg._float_values[1] = 0.0;
	msg._float_values[2] = 0.0;

	switch (msg._type)
	{
		case CommandServer::Message::MSG_GPS_POSITION:
		{
			char buf[4];

			for (int i = 0; i < 3; i++)
			{
				stream.read((char*)&buf, 4);
				msg._float_values[i] = ntohl((float&)buf);
			}
			break;
		}

		case CommandServer::Message::MSG_SCRIPT:
		{
			char buf[4];
			stream.read((char*)&buf, 4);
			uint32_t len = ntohl((uint32_t&)buf);

			char script_buf[len];
			stream.read((char*)&script_buf, len);
			msg._data.write((char*)&script_buf, len);
			break;
		}

		default:
			break;
	}
}

CommandServer::CommandServer(unsigned int port)
 : _srv(), _running(true), _active_connections(0)
{
	_srv.bind(port);
}

CommandServer::~CommandServer()
{
	_srv.shutdown();
	_srv.close();
	interrupt();

	// wait until all connections are closed
	ibrcommon::MutexLock l(_active_connections_cond);
	while (_active_connections > 0) _active_connections_cond.wait();
}

void CommandServer::setup()
{
	_srv.listen(5);
}

void CommandServer::run()
{
	while (_running)
	{
		ibrcommon::tcpstream *stream = _srv.accept();
		CommandServer::Connection *conn = new CommandServer::Connection(stream, _active_connections_cond, _active_connections);
		conn->start();
	}
}

void CommandServer::finally()
{
}
