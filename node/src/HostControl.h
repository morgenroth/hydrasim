/*
 * HostControl.h
 *
 *  Created on: 17.01.2011
 *      Author: morgenro
 */

#ifndef HOSTCONTROL_H_
#define HOSTCONTROL_H_

#include <string>

class HostControl
{
public:
	static HostControl& getInstance();
	virtual ~HostControl();

	void shutdown() const;
	void system(const std::string&) const;

private:
	HostControl();
	bool _harmless;
};

#endif /* HOSTCONTROL_H_ */
