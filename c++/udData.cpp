#include<iostream>
#include<vector>
#include<sstream>
#include<fstream>
#include<zlib.h>
#include<iterator>
using namespace std;
void split(const string& str,const string& delim, vector<string>& res)
{
    if("" == str)
        return;
    string strs = str + delim;
    size_t pos;
    size_t size = strs.size();
    for (int i = 0; i < size; ++i)
    {
        pos = strs.find(delim, i);
        if( pos < size)
        {
            string s = strs.substr(i, pos - i);
            res.push_back(s);
            i = pos + delim.size() - 1;
        }
    }
}
void getElement(string& line, const string& strID, string& str)
{
    int begin = line.find(strID);
    int end = line.find(",", begin);
    str = line.substr(begin + strID.length(), end - begin - strID.length());
}
void readLineToGZ(const char* const path, vector<string>& line_vec)
{
    gzFile gzfp = gzopen(path, "rb");
    string str = "";
    char buffer[100000];
    char* c;
    while (true)
    {
        int err;
        if ((c = gzgets(gzfp,buffer,100000)))
        {
            string str(buffer);
            line_vec.push_back(str);
        }
        if(c==NULL)
        {
            cerr<<gzerror(gzfp, &err)<<endl;
            break;
        }
    }
    gzclose(gzfp);
}
void  getFilePath(const string& input,vector<string>& filepath_vec)
{
    fstream f(input);
    string line;
    while(getline(f, line))
    {
        filepath_vec.push_back(line);
    }
    f.close();
}
bool endswith(const std::string& str, const std::string& end)
{
    int srclen = str.size();
    int endlen = end.size();
    if (srclen >= endlen)
    {
        string temp = str.substr(srclen - endlen, endlen);
        if (temp == end)
            return true;
    }
    return false;
}
string&   replace_all_distinct(string&   str,const   string&   old_value,const   string&   new_value)
{
    for(string::size_type   pos(0);   pos!=string::npos;   pos+=new_value.length())   {
        if(   (pos=str.find(old_value,pos))!=string::npos   )
            str.replace(pos,old_value.length(),new_value);
        else   break;
    }
    return   str;
}
void getDateTime(const string& str,string& datetime)
{
    datetime = str.substr(2,10) + " " + str.substr(28,8);
    datetime = replace_all_distinct(datetime,"_","-");
}
void parseGZFile(const char* const input, const string& output,vector<string>& field_vec)
{   
    vector<string> lines;
    cout<<"开始读取:"<<input<<endl;
    readLineToGZ(input, lines);
    string context;
    ofstream out;
    out.open(output, ios::app);
	for(vector<string>::iterator iters=lines.begin();iters!=lines.end();iters++)
    {
        for(vector<string>::iterator iter= field_vec.begin();iter!=field_vec.end();iter++)
        {
            getElement(*iters, *iter, context);
            out<<*iter<<context<<";";
        }
        out<<endl;
    }
    cout<<"处理成功:"<<input<<endl;
    out.close();
}
void parseLogFile(const string& input, const string& output,vector<string>& field_vec)
{
    fstream f(input);
    string line;
    cout<<"开始读取:"<<input<<endl;
    string context;
    ofstream out;
    out.open(output, ios::app);
    while(getline(f, line))
    {
        string date;
        getDateTime(line, date);
        out<<"datetime:"<<date<<",";
        for(vector<string>::iterator iter= field_vec.begin();iter!=field_vec.end();iter++)
        {
            getElement(line, *iter, context);
            out<<*iter<<context<<",";
        }
        out<<endl;
    }
    cout<<"处理成功:"<<input<<endl;
    f.close();
    out.close();
}

bool LogOrGZFile(const string& filepath)
{
    return endswith(filepath, ".log");    
}

//./test path.txt output.txt ip name
int main(int argc, char const *argv[])
{
	if(argc<3)
	{
		cout<<"USAGE:./udsvrData path.txt output.txt <> <> ..."<<endl;
		return 0;
	}
    vector<string> fields;
    for (int i=3; i<argc;i++)
    {
        fields.push_back(argv[i]);
    }
     parseLogFile(argv[1],argv[2],fields);
    /*
    vector<string> path_vec,fields;
    for(int i=3;i<argc;i++)
    {
        fields.push_back(argv[i]);
    }
    getFilePath(argv[1],path_vec);
    for(vector<string>::iterator iter=path_vec.begin();iter!=path_vec.end();iter++)
    {
        if(LogOrGZFile(*iter))
        {
            parseLogFile((*iter).c_str(), argv[2], fields);    
        }
        else
        {
            parseGZFile((*iter).c_str(), argv[2], fields);
        }
    }*/
    return 0;
}
