/*
 * FakeGPS.h
 *
 *  Created on: 17.01.2011
 *      Author: morgenro
 */

#ifndef FAKEGPS_H_
#define FAKEGPS_H_

class FakeGPS
{
public:
	enum GPS_STATE
	{
		GPS_STATE_DISABLED = 0,
		GPS_STATE_INITIAL = 1,
		GPS_STATE_GOT_FIX = 2
	};

	static FakeGPS& getInstance();
	virtual ~FakeGPS();

	GPS_STATE getState() const;

	void disable();

	void getPosition(float &lon, float &lat) const;

	void getPosition(float &lon, float &lat, float &alt) const;

	void setPosition(const float &lon, const float &lat, const float &alt);

private:
	FakeGPS();

	double _lon, _lat, _alt;

	GPS_STATE _state;
};

#endif /* FAKEGPS_H_ */
