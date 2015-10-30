/*
 * Copyright (c) 2013-2015, Roland Bock
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification,
 * are permitted provided that the following conditions are met:
 *
 *   Redistributions of source code must retain the above copyright notice, this
 *   list of conditions and the following disclaimer.
 *
 *   Redistributions in binary form must reproduce the above copyright notice, this
 *   list of conditions and the following disclaimer in the documentation and/or
 *   other materials provided with the distribution.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 * ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 * WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 * (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 * LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
 * ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

#ifndef SQLPP_DETAIL_WRAP_OPERAND_H
#define SQLPP_DETAIL_WRAP_OPERAND_H

namespace sqlpp
{
  template <typename T, typename Enable = void>
  struct wrap_operand
  {
    using type = T;
  };

  template <typename T>
  using wrap_operand_t = typename wrap_operand<T>::type;
}

#include <date.h>
#include <string>
#include <sqlpp11/date_time_fwd.h>
#include <sqlpp11/serializer.h>
#include <sqlpp11/type_traits.h>
#include <sqlpp11/basic_expression_operators.h>
#include <sqlpp11/alias_operators.h>

namespace sqlpp
{
  struct integral;

  struct day_point_operand : public alias_operators<day_point_operand>
  {
    using _traits = make_traits<day_point, tag::is_expression, tag::is_wrapped_value>;
    using _nodes = detail::type_vector<>;
    using _is_aggregate_expression = std::true_type;

    using _value_t = ::sqlpp::chrono::day_point;

    day_point_operand() : _t{}
    {
    }

    day_point_operand(_value_t t) : _t(t)
    {
    }

    day_point_operand(const day_point_operand&) = default;
    day_point_operand(day_point_operand&&) = default;
    day_point_operand& operator=(const day_point_operand&) = default;
    day_point_operand& operator=(day_point_operand&&) = default;
    ~day_point_operand() = default;

    bool _is_trivial() const
    {
      return _t == _value_t{};
    }

    _value_t _t;
  };

  template <typename Context>
  struct serializer_t<Context, day_point_operand>
  {
    using _serialize_check = consistent_t;
    using Operand = day_point_operand;

    static Context& _(const Operand& t, Context& context)
    {
      const auto ymd = ::date::year_month_day{t._t};
      context << "DATE '" << ymd << "'";
      return context;
    }
  };

  template <typename Period>
  struct time_point_operand : public alias_operators<time_point_operand<Period>>
  {
    using _traits = make_traits<time_point, tag::is_expression, tag::is_wrapped_value>;
    using _nodes = detail::type_vector<>;
    using _is_aggregate_expression = std::true_type;

    using _value_t = std::chrono::time_point<std::chrono::system_clock, Period>;

    time_point_operand() : _t{}
    {
    }

    time_point_operand(_value_t t) : _t(t)
    {
    }

    time_point_operand(const time_point_operand&) = default;
    time_point_operand(time_point_operand&&) = default;
    time_point_operand& operator=(const time_point_operand&) = default;
    time_point_operand& operator=(time_point_operand&&) = default;
    ~time_point_operand() = default;

    bool _is_trivial() const
    {
      return _t == _value_t{};
    }

    _value_t _t;
  };

  template <typename Context, typename Period>
  struct serializer_t<Context, time_point_operand<Period>>
  {
    using _serialize_check = consistent_t;
    using Operand = time_point_operand<Period>;

    static Context& _(const Operand& t, Context& context)
    {
      const auto dp = ::date::floor<::date::days>(t._t);
      const auto time = ::date::make_time(t._t - dp);
      const auto ymd = ::date::year_month_day{dp};
      context << "TIMESTAMP '" << ymd << ' ' << time << "'";
      return context;
    }
  };

  template <typename Period>
  struct wrap_operand<std::chrono::time_point<std::chrono::system_clock, Period>, void>
  {
    using type = time_point_operand<Period>;
  };

  template <>
  struct wrap_operand<std::chrono::time_point<std::chrono::system_clock, sqlpp::chrono::days>, void>
  {
    using type = day_point_operand;
  };
}

#endif
