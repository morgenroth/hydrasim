/*
 * HostControl.cpp
 *
 *  Created on: 17.01.2011
 *      Author: morgenro
 */

#include "HostControl.h"
#include <iostream>
#include <cstdlib>

HostControl& HostControl::getInstance()
{
	static HostControl hc;
	return hc;
}

HostControl::HostControl()
 : _harmless(false)
{
}

HostControl::~HostControl()
{
}

void HostControl::shutdown() const
{
	std::cout << "shutdown the node" << std::endl;

	if (!_harmless)
	{
		::system("halt");
	}
}

void HostControl::system(const std::string &cmd) const
{
	std::cout << "system call: " << cmd << std::endl;

	if (!_harmless)
	{
		int ret = ::system(cmd.c_str());
	}
}
