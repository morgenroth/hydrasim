/*
 * Configuration.cpp
 *
 *  Created on: 14.01.2011
 *      Author: morgenro
 */

#include "Configuration.h"
#include "unistd.h"

Configuration::Configuration()
{
	// TODO Auto-generated constructor stub

}

Configuration::~Configuration()
{
	// TODO Auto-generated destructor stub
}

const std::string Configuration::getHostname() const
{
	char *hostname_array = new char[64];

	if ( gethostname(hostname_array, 64) != 0 )
	{
		// error
		delete[] hostname_array;
		return "unknown";
	}

	std::string hostname(hostname_array);
	delete[] hostname_array;

	return hostname;
}
