#include<iostream>
#include<fstream>
#include<sstream>
#include<string>
#include <iconv.h>
using namespace std;

bool is_str_utf8(const char* str)
{
	unsigned int nBytes = 0;
	unsigned char chr = *str;
	bool bAllAscii = true;
	for (unsigned int i = 0; str[i] != '\0'; ++i){
		chr = *(str + i);
		if (nBytes == 0 && (chr & 0x80) != 0){
			bAllAscii = false;
		}
		if (nBytes == 0) {
			if (chr >= 0x80) {
 
				if (chr >= 0xFC && chr <= 0xFD){
					nBytes = 6;
				}
				else if (chr >= 0xF8){
					nBytes = 5;
				}
				else if (chr >= 0xF0){
					nBytes = 4;
				}
				else if (chr >= 0xE0){
					nBytes = 3;
				}
				else if (chr >= 0xC0){
					nBytes = 2;
				}
				else{
					return false;
				}
				nBytes--;
			}
		}
		else{
			if ((chr & 0xC0) != 0x80){
				return false;
			}
			nBytes--;
		}
	}
	if (nBytes != 0)  {
		return false;
	}
	if (bAllAscii){
		return true;
	}
	return true;
}
bool is_str_gbk(const char* str)
{
	unsigned int nBytes = 0;
	unsigned char chr = *str;
	bool bAllAscii = true;
	for (unsigned int i = 0; str[i] != '\0'; ++i){
		chr = *(str + i);
		if ((chr & 0x80) != 0 && nBytes == 0){
			bAllAscii = false;
		}
		if (nBytes == 0) {
			if (chr >= 0x80) {
				if (chr >= 0x81 && chr <= 0xFE){
					nBytes = +2;
				}
				else{
					return false;
				}
				nBytes--;
			}
		}
		else{
			if (chr < 0x40 || chr>0xFE){
				return false;
			}
			nBytes--;
		}
	}
	if (nBytes != 0)  {
		return false;
	}
	if (bAllAscii){
		return true;
	}
	return true;
}
std::string code_convert(char *source_charset, char *to_charset, const std::string& sourceStr)
{
	iconv_t cd = iconv_open(to_charset, source_charset);
	if (cd == 0)
		return "";
	size_t inlen = sourceStr.size();
	size_t outlen = 255;
	char* inbuf = (char*)sourceStr.c_str();
	char outbuf[255];//这里实在不知道需要多少个字节，这是个问题
	memset(outbuf, 0, outlen);
	char *poutbuf = outbuf;
	if (iconv(cd, &inbuf, &inlen, &poutbuf,&outlen) == -1)
		return "";
	std::string strTemp(outbuf);//此时的strTemp为转换编码之后的字符串
	iconv_close(cd);
	return strTemp;
}
 
std::string Utf8ToGbk(const std::string& strUtf8)
{
	return code_convert("utf-8", "gb2312", strUtf8);
}
 
std::string UnicodeToGbk(const std::string& strGbk)// 传入的strGbk是GBK编码 
{
	return code_convert("UCS-2LE", "gb2312",strGbk);
}
int main()
{
	fstream f("");
	string line;
	while(getline(f, line))
	{
		if(is_str_gbk(line))
		{
			out>>line>>endl;
		}else if(is_str_utf8(line))
		{
			
		}
	}
	return 0;
}
