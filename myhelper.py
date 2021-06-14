import json
import time
import random as rd

import config


def rand_sleep():
    rand_time = rd.uniform(config.PAYMENTS_TIMEOUT[0], config.PAYMENTS_TIMEOUT[1])
    time.sleep(rand_time)


def calc_mult_payments(sum_to_send, max_sum):
    def add_info(array, summ):
        summ = round(summ, 2)
        if array["info"].get(summ):
            array["info"][summ] += 1
        else:
            array["info"][summ] = 1
        return array

    try:
        if not sum_to_send or not max_sum or max_sum > sum_to_send:
            raise ValueError

        max_sum = float(max_sum)
        sum_to_send = float(sum_to_send)
        sums = {"info": {}, "payments":[]}
        while sum_to_send:
            if sum_to_send >= 1 and sum_to_send - max_sum > 0:
                sum_to_send -= max_sum
                sums["payments"].append(round(max_sum, 2))
                sums = add_info(sums, max_sum)
            else:
                if 1 > sum_to_send > 0:
                    last_payment = sums["payments"].pop()
                    sum_left = last_payment + sum_to_send
                    # Убираем лишнюю инфу.
                    sums["info"][last_payment] -= 1

                    sums["payments"].append(round(sum_left / 2, 2))
                    sums["payments"].append(round(sum_left - sums["payments"][-1], 2))

                    sums = add_info(sums, round(sum_left / 2, 2))
                    sums = add_info(sums, sum_left - sums["payments"][-2])
                elif max_sum - sum_to_send >= 1 or sum_to_send - max_sum == 0:
                    sums["payments"].append(round(sum_to_send, 2))
                    sums = add_info(sums, sum_to_send)
                    break
                else:
                    raise ValueError
                break
        return sums
    except:
        pass


if __name__ == "__main__":
    rand_sleep()
