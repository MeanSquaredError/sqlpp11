#pragma once

/*
 * Copyright (c) 2021-2021, Roland Bock, ZerQAQ
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

#include <sqlpp11/update.h>
#include <sqlpp11/limit.h>
#include <sqlpp11/order_by.h>

namespace sqlpp
{
  namespace mysql
  {
    template <typename Database>
    using blank_update_t = statement_t<Database,
                                       update_t,
                                       no_single_table_t,
                                       no_update_list_t,
                                       no_where_t<true>,
                                       no_order_by_t,
                                       no_limit_t>;

    template <typename Table>
    constexpr auto update(Table table) -> decltype(blank_update_t<void>().single_table(table))
    {
      return {blank_update_t<void>().single_table(table)};
    }

    template <typename Database, typename Table>
    constexpr auto dynamic_update(const Database& /*unused*/, Table table)
        -> decltype(blank_update_t<Database>().single_table(table))
    {
      static_assert(std::is_base_of<connection_base, Database>::value, "Invalid database parameter");
      return {blank_update_t<Database>().single_table(table)};
    }
  }  // namespace mysql
}  // namespace sqlpp
