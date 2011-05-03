/*
 * Configuration.h
 *
 *  Created on: 14.01.2011
 *      Author: morgenro
 */

#ifndef CONFIGURATION_H_
#define CONFIGURATION_H_

#include <string>

class Configuration
{
public:
	Configuration();
	virtual ~Configuration();

	const std::string getHostname() const;
};

#endif /* CONFIGURATION_H_ */
