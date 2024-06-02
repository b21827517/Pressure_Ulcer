// Boost.Geometry

// Copyright (c) 2021, Oracle and/or its affiliates.

// Contributed and/or modified by Adam Wulkiewicz, on behalf of Oracle

// Licensed under the Boost Software License version 1.0.
// http://www.boost.org/users/license.html

#ifndef BOOST_GEOMETRY_STRATEGY_GEOGRAPHIC_AREA_BOX_HPP
#define BOOST_GEOMETRY_STRATEGY_GEOGRAPHIC_AREA_BOX_HPP


#include <boost/geometry/core/radian_access.hpp>
#include <boost/geometry/srs/spheroid.hpp>
#include <boost/geometry/strategies/spherical/get_radius.hpp>
#include <boost/geometry/strategy/area.hpp>
#include <boost/geometry/util/normalize_spheroidal_box_coordinates.hpp>


namespace boost { namespace geometry
{

namespace strategy { namespace area
{

// Based on the approach for spherical coordinate system:
// https://math.stackexchange.com/questions/131735/surface-element-in-spherical-coordinates
// http://www.cs.cmu.edu/afs/cs/academic/class/16823-s16/www/pdfs/appearance-modeling-3.pdf
// https://www.astronomyclub.xyz/celestial-sphere-2/solid-angle-on-the-celestial-sphere.html
// https://mathworld.wolfram.com/SolidAngle.html
// https://en.wikipedia.org/wiki/Spherical_coordinate_system
// and equations for spheroid:
// https://en.wikipedia.org/wiki/Geographic_coordinate_conversion
// https://en.wikipedia.org/wiki/Meridian_arc
// Note that the equations use geodetic latitudes so we do not have to convert them.
// assume(y_max > y_min);
// assume(x_max > x_min);
// M: a*(1-e^2) / (1-e^2*sin(y)^2)^(3/2);
// N: a / sqrt(1-e^2*sin(y)^2);
// O: N*cos(y)*M;
// tellsimp(log(abs(e*sin(y_min)+1)), p_min);
// tellsimp(log(abs(e*sin(y_min)-1)), m_min);
// tellsimp(log(abs(e*sin(y_max)+1)), p_max);
// tellsimp(log(abs(e*sin(y_max)-1)), m_max);
// S: integrate(integrate(O, y, y_min, y_max), x, x_min, x_max);
// combine(S);
//
// An alternative solution to the above formula was suggested by Charles Karney
// https://github.com/boostorg/geometry/pull/832
// The following are formulas for area of a box defined by the equator and some latitude,
// not arbitrary box.
// For e^2 > 0
// dlambda*b^2*sin(phi)/2*(1/(1-e^2*sin(phi)^2) + atanh(e*sin(phi))/(e*sin(phi)))
// For e^2 < 0
// dlambda*b^2*sin(phi)/2*(1/(1-e^2*sin(phi)^2) + atan(ea*sin(phi))/(ea*sin(phi)))
// where ea = sqrt(-e^2)
template
<
    typename Spheroid = srs::spheroid<double>,
    typename CalculationType = void
>
class geographic_box
{
public:
    template <typename Box>
    struct result_type
        : strategy::area::detail::result_type
            <
                Box,
                CalculationType
            >
    {};

    geographic_box() = default;

    explicit geographic_box(Spheroid const& spheroid)
        : m_spheroid(spheroid)
    {}

    template <typename Box>
    inline auto apply(Box const& box) const
    {
        typedef typename result_type<Box>::type return_type;

        return_type const c0 = 0;

        return_type x_min = get_as_radian<min_corner, 0>(box); // lon
        return_type y_min = get_as_radian<min_corner, 1>(box); // lat
        return_type x_max = get_as_radian<max_corner, 0>(box);
        return_type y_max = get_as_radian<max_corner, 1>(box);

        math::normalize_spheroidal_box_coordinates<radian>(x_min, y_min, x_max, y_max);

        if (x_min == x_max || y_max == y_min)
        {
            return c0;
        }

        return_type const e2 = formula::eccentricity_sqr<return_type>(m_spheroid);

        return_type const x_diff = x_max - x_min;
        return_type const sin_y_min = sin(y_min);
        return_type const sin_y_max = sin(y_max);

        if (math::equals(e2, c0))
        {
            // spherical formula
            return_type const a = get_radius<0>(m_spheroid);
            return x_diff * (sin_y_max - sin_y_min) * a * a;
        }

        return_type const c1 = 1;
        return_type const c2 = 2;
        return_type const b = get_radius<2>(m_spheroid);

        /*
        return_type const c4 = 4;
        return_type const e = math::sqrt(e2);

        return_type const p_min = log(math::abs(e * sin_y_min + c1));
        return_type const p_max = log(math::abs(e * sin_y_max + c1));
        return_type const m_min = log(math::abs(e * sin_y_min - c1));
        return_type const m_max = log(math::abs(e * sin_y_max - c1));
        return_type const n_min = e * sin_y_min * sin_y_min;
        return_type const n_max = e * sin_y_max * sin_y_max;
        return_type const d_min = e * n_min - c1;
        return_type const d_max = e * n_max - c1;

        // NOTE: For equal latitudes the original formula generated by maxima may give negative
        //   result. It's caused by the order of operations, so here they're rearranged for
        //   symmetry.
        return_type const comp0 = (p_min - m_min) / (c4 * e * d_min);
        return_type const comp1 = sin_y_min / (c2 * d_min);
        return_type const comp2 = n_min * (m_min - p_min) / (c4 * d_min);
        return_type const comp3 = (p_max - m_max) / (c4 * e * d_max);
        return_type const comp4 = sin_y_max / (c2 * d_max);
        return_type const comp5 = n_max * (m_max - p_max) / (c4 * d_max);
        return_type const comp02 = comp0 + comp1 + comp2;
        return_type const comp35 = comp3 + comp4 + comp5;

        return b * b * x_diff * (comp02 - comp35);
        */

        return_type const comp0_min = c1 / (c1 - e2 * sin_y_min * sin_y_min);
        return_type const comp0_max = c1 / (c1 - e2 * sin_y_max * sin_y_max);

        // NOTE: For latitudes equal to 0 the original formula returns NAN
        return_type comp1_min = 0, comp1_max = 0;
        if (e2 > c0)
        {
            return_type const e = math::sqrt(e2);
            return_type const e_sin_y_min = e * sin_y_min;
            return_type const e_sin_y_max = e * sin_y_max;

            comp1_min = e_sin_y_min == c0 ? c1 : atanh(e_sin_y_min) / e_sin_y_min;
            comp1_max = e_sin_y_max == c0 ? c1 : atanh(e_sin_y_max) / e_sin_y_max;
        }
        else
        {
            return_type const ea = math::sqrt(-e2);
            return_type const ea_sin_y_min = ea * sin_y_min;
            return_type const ea_sin_y_max = ea * sin_y_max;

            comp1_min = ea_sin_y_min == c0 ? c1 : atan(ea_sin_y_min) / ea_sin_y_min;
            comp1_max = ea_sin_y_max == c0 ? c1 : atan(ea_sin_y_max) / ea_sin_y_max;
        }

        return_type const comp01_min = sin_y_min * (comp0_min + comp1_min);
        return_type const comp01_max = sin_y_max * (comp0_max + comp1_max);

        return b * b * x_diff * (comp01_max - comp01_min) / c2;
    }

    Spheroid model() const
    {
        return m_spheroid;
    }

private:
    Spheroid m_spheroid;
};


}} // namespace strategy::area


}} // namespace boost::geometry


#endif // BOOST_GEOMETRY_STRATEGY_GEOGRAPHIC_AREA_BOX_HPP
