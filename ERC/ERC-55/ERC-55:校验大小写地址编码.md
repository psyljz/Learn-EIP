# ERC-55:校验大小写地址编码

## Why ？

这是一个 2016年1月14日，Vitalik Buterin，Alex Van de Sande创建的[提案](https://eips.ethereum.org/EIPS/eip-55)。是为了防止在输入或者更改地址的情况下出现人为的输入错误，巧妙的利用十六进制数字的大小写进行了检验，以确定这是一个正确的转账地址，没有人为的输入错误。由于ICAP([更多资料](https://www.jianshu.com/p/fa8465bbd967))方案一直开发缓慢，EIP-55得到了广泛的应用。

## What

改变原始地址中用字母表示的数字的大小写来校验。

|          | ETH地址                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------------ |
| 原始地址 | 0xf1299**eb**148b413b**e**971822**d**f**f**4f**d**079d**ab**9d045d |
| EIP-55   | 0xf1299**EB**148b413b**E**971822**D**f**F**4f**D**079d**AB**9d045d |

- 每个地址平均有 15 个校验位，如果输入错误，随机生成的地址意外通过校验的净概率为 0.0247%。可靠性很好，随机地址只有万分之二的概率可以通过检验。
- 地址可以保持原有的长度，不用新增校验位。

## How

### 编码

1. 得到原始地址，对其使用keccak256进行哈希运算，取结果的前20个字节。

- 以 `0xf1299eb148b413be971822dff4fd079dab9d045d`为例
- 进行哈希运算之后得到: 用十六进制表示的32个字节的哈希值 `2bc188b1f661ad0cc363d2f4be284e96ecc3851590930eada61a200e8ae539a3`
- 只取前20个字节
- `2bc188b1f661ad0cc363d2f4be284e96ecc38515`

按照[官方文档](https://eips.ethereum.org/EIPS/eip-55)的描述转换规则

> In English, convert the address to hex, but if the `i`th digit is a letter (ie. it’s one of `abcdef`) print it in uppercase if the `4*i`th bit of the hash of the lowercase hexadecimal address is 1 otherwise print it in lowercase.

刚开始很懵逼，后来才明白其对照的是二进制的进行描述的。

- 我们也相应的将哈希值转化为二进制 `0010101111000001100010001011000111110110011000011010110100001100110000110110001111010010111101001011111000101000010011101001011011101100110000111000010100010101100100001001001100001110101011011010011000011010001000000000111010001010111001010011100110100011`
- 转化规则如下：
  - 如果原始地址中 `i`位置数字是用字母表示的，则检查相应的哈希值 `4*i`位置的二进制是否为1。
  - 如果为1，则把该位置的字母大写，否则小写
- 通过编码这个原始地址作为例子，来说明转化的过程
  - 0x**f**1299eb148b413be971822dff4fd079dab9d045d
  - 我们依次检查原始地址，发现第一个字母就为字母，为第0位，检查相对应的二进制位4*0位置的数字，结果发现为0。
  - **0**010101111000001100010001011000111110110011000011010110100001100110000110110001111010010111101001011111000101000010011101001011011101100110000111000010100010101100100001001001100001110101011011010011000011010001000000000111010001010111001010011100110100011
  - 所以保持小写，我们继续。
  - 0x**f**1299**e**b148b413be971822dff4fd079dab9d045d
  - 发现第5位为字母e，检查相对应的二进制位4*5位置的数字，结果发现为1。
  - **0**0101011110000011000***1***0001011000111110110011000011010110100001100110000110110001111010010111101001011111000101000010011101001011011101100110000111000010100010101100100001001001100001110101011011010011000011010001000000000111010001010111001010011100110100011
  - 所以，字母e转变为大写。
  - 挨个按照规则转化完毕所有字母，就可以得到一个使用大小写检验编码的地址。

|          | ETH地址                                                                                                |
| -------- | ------------------------------------------------------------------------------------------------------ |
| 原始地址 | 0xf1299**eb**148b413b**e**971822**d**f**f**4f**d**079d**ab**9d045d |
| EIP-55   | 0xf1299**EB**148b413b**E**971822**D**f**F**4f**D**079d**AB**9d045d |

### Tips

- 检查相对应的二进制位 `4*i`位置的数字是否为1其实就是检查原始地址的哈希值的十六进制的相应 `i`位置的数字是否大于等于8。因为每4个二进制数表示一个十六进制数，如果4个二进制数开头位为1，那么这个数大于等于8。因此代码的实现一般也是通过和8的比大小来决定。

### 解码

- 目前在钱包中都内置了EIP-55的校验，如果向一个通不过检验的地址转账，会提示地址无效。
- 校验的过程如下：
  1. 把地址全部恢复成小写
  2. 计算哈希值
  3. 检查对应的规则是否符合
- 解码代码 例子

```python

# 判断所给地址是否能够通过检验
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
           
            checksummed_buffer += character  
        elif character in "abcdef":  
            # 检查相应的数字是否大于8  
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

	##### 在此输入你的地址，更改任意一个数字或者字母大小写都无法通过校验
    address = "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed"  
    ##### 在此输入你的地址
    if decode(address):  
        print("***",address,"***","合法地址")  
    else:  
        print("***",address,"***","非法地址")
```

## 参考资料

1. Vitalik Buterin [[vitalik.buterin@ethereum.org](mailto:vitalik.buterin@ethereum.org)](%5Bvitalik.buterin@ethereum.org%5D(mailto:vitalik.buterin@ethereum.org)), Alex Van de Sande [[avsa@ethereum.org](mailto:avsa@ethereum.org)](%5Bavsa@ethereum.org%5D(mailto:avsa@ethereum.org)), "EIP-55: Mixed-case checksum address encoding," _Ethereum Improvement Proposals_, no. 55, January 2016. [Online serial]. Available: https://eips.ethereum.org/EIPS/eip-55.
