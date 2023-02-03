import eth_utils


def decode(addr_str):
    addr = eth_utils.to_bytes(hexstr=addr_str)
    # 1.把地址全部恢复成小写
    hex_addr = addr.hex()
    checksummed_buffer = ""

    # 2. 计算哈希值
    hashed_address = eth_utils.keccak(text=hex_addr).hex()

    # 计算正确的地址
    for nibble_index, character in enumerate(hex_addr):

        if character in "0123456789":
            # We can't upper-case the decimal digits
            checksummed_buffer += character
        elif character in "abcdef":
            # Check if the corresponding hex digit (nibble) in the hash is 8 or higher
            hashed_address_nibble = int(hashed_address[nibble_index], 16)
            if hashed_address_nibble > 7:
                checksummed_buffer += character.upper()
            else:
                checksummed_buffer += character
        else:
            raise eth_utils.ValidationError(
                f"Unrecognized hex character {character!r} at position {nibble_index}"
            )

    # 3.判断地址是否一致
    return addr_str == "0x" + checksummed_buffer


# 地址字符串

if __name__ == '__main__':
    address = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"
    if decode(address):
        print("***",address,"***","合法地址")
    else:
        print("***",address,"***","非法地址")
