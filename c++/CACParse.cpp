#include<iostream>
#include<sstream>
#include<vector>
#include<map>
#include<fstream>
#include<set>
#include<string>
#include<zlib.h>
#include<cstdlib>
using namespace std;

vector<string> table = { "@gmail.com", "@qq.com", "@163.com", "@proton.com", "@foxmail.com",
                                                "@yahoo", "@hotmail.com", "@189.cn", "@aliyun.com","@126.com",
                                                "@msn.com", "@yeah.net" };

vector<string>  split(const string& str, const string& delim)
{
    vector<string> res;
    if ("" == str) return  res;
    string strs = str + delim;
    size_t pos;
    size_t size = strs.size();
    for (int i = 0; i < size; ++i)
    {
        pos = strs.find(delim, i);
        if (pos < size)
        {
            string s = strs.substr(i, pos - i);
            res.push_back(s);
            i = pos + delim.size() - 1;
        }
    }
    return res;
}

string&   replace_all_distinct(string&   str, const   string&   old_value, const   string&   new_value)
{
    for (string::size_type pos(0); pos != string::npos; pos += new_value.length()) {
        if ((pos = str.find(old_value, pos)) != string::npos)
            str.replace(pos, old_value.length(), new_value);
        else   break;
    }
    return   str;
}

bool startswith(const std::string& str, const std::string& start)
{
    int srclen = str.size();
    int startlen = start.size();
    if (srclen >= startlen)
    {
        string temp = str.substr(0, startlen);
        if (temp == start)
            return true;
    }
    return false;
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
void getElement(string& line, const string& strID, string& str)
{
    int begin = line.find(strID);
    int end = line.find(",", begin);
    str = line.substr(begin + strID.length(), end - begin - strID.length());
}

bool hasInTable(string& str)
{
    bool flag = false;
    vector<string>::iterator iter = table.begin();
    for (; iter != table.end(); iter++)
    {
        if (*iter == str)
            flag = true;
    }
    return flag;
}
void readLineToGZ(const char* const path, vector<string>& line_vec)
{
        gzFile gzfp = gzopen(path, "rb");
        string str = "";
        char buffer[100000];
    char* c;
        while (!gzeof(gzfp))
        {
                if ((c = gzgets(gzfp,buffer,100000)))
                {
            //cout<<buffer<<endl;
            string str(buffer);
            cout<<str<<endl;
                        line_vec.push_back(str);
                }
        }
}

void parseGZFile(const char* const input, const string& output1, const string& output2)
{   
        vector<map<string, string>> result_vec;
        vector<string> lines;
        cout<<"开始读取:"<<input<<endl;
        readLineToGZ(input, lines);
        int pos;
        string authuser, sender, rcpt, tag;
        ofstream out1,out2;
        out1.open(output1, ios::app);
    out2.open(output2, ios::app);
    bool flag=false;
        for(vector<string>::iterator iter=lines.begin();iter!=lines.end();iter++)
        {
                map<string, string> result;
                getElement(*iter, "authuser:", authuser);
                getElement(*iter, "sender:", sender);
                getElement(*iter, "rcpt:", rcpt);
                getElement(*iter, "tag:", tag);
                //result.insert(pair<string, string>("sender", sender));
                //result.insert(pair<string, string>("tag", tag));
                pos= rcpt.rfind(";",rcpt.size()-1);
                rcpt =rcpt.substr(0,pos);
                //result.insert(pair<string, string>("rcpt", rcpt));
                //result_vec.push_back(result);
        for(int i=0;i<table.size();i++)
        {
            if(rcpt.find(table[i])!=string::npos)
            {
                flag = true;
                break;
            }
        }
        if(!flag && sender!="" && sender!=" " && rcpt!="" && rcpt!=" ")
                {       if( authuser!=" "&& authuser!= "")
                                out1<<rcpt<<" "<<sender<<" "<<tag<<endl;
                        else
                                out2<<rcpt<<" "<<sender<<" "<<tag<<endl;
                }
        else
            flag= false;
        }
    cout<<"处理成功:"<<input<<endl;
}

//由于数据过大，故意采用局部处理
void parseLogFile(const string& input, const string& output1, const string& output2)
{
    vector<map<string, string>> result_vec;
    fstream f(input);
        int pos;
        string sender, rcpt, tag, authuser;
        ofstream out1,out2;
        out1.open(output1, ios::app);
    out2.open(output2, ios::app);
        bool flag=false;
    string line;
    cout<<"开始读取:"<<input<<endl;
        while(getline(f, line))
        {
                map<string, string> result;
        getElement(line, "authuser:", authuser);
                getElement(line, "sender:", sender);
                getElement(line, "rcpt:", rcpt);
                getElement(line, "tag:", tag);
                //result.insert(pair<string, string>("sender", sender));
                //result.insert(pair<string, string>("tag", tag));
                pos= rcpt.rfind(";",rcpt.size()-1);
                rcpt =rcpt.substr(0,pos);
                //result.insert(pair<string, string>("rcpt", rcpt));
                //result_vec.push_back(result);
                for(int i=0;i<table.size();i++)
                {
                        if(rcpt.find(table[i])!=string::npos)
                        {
                                flag = true;
                                break;
                        }
                }
                if(!flag && sender!="" && sender!=" " && rcpt!="" && rcpt!=" ")
                {    if( authuser!=" "&& authuser!= "")
                out1<<rcpt<<" "<<sender<<" "<<tag<<endl;
            else
                out2<<rcpt<<" "<<sender<<" "<<tag<<endl;
                }
                else
                        flag= false;
        }
        cout<<"处理成功:"<<input<<endl;

}
//读取路径文件
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
//1代表是log 0代表是gz文件
bool LogOrGZFile(const string& filepath)
{
    return endswith(filepath, ".log");    
}

string int2str(const int &int_temp)
{
    string s;
    stringstream stream;
    stream<<int_temp;
    s=stream.str();
    return s;
}
int main(int argc, char **argv)
{
    if (argc < 2)
    {
        cout << "USAGE:./a.out path" << endl;
        exit(-1);
    }
    
    vector<string> path_vec;
    getFilePath(argv[1], path_vec);
    int count=1;
    for(vector<string>::iterator iter=path_vec.begin();iter!=path_vec.end();iter++)
    {
        string output1=int2str((count/30+500))+"_authuser.txt";
        string output2=int2str((count/30+500))+".txt";
        //if(LogOrGZFile(*iter))
        //{
            //parseLogFile((*iter).c_str(), output1, output2);    
        //}
        //else
        //{
            parseGZFile((*iter).c_str(), output1, output2);
        //}*/
        count++;
    }
    //parseGZFile(argv[1],"ppp.txt");
    //parseLogFile(argv[1], "result.txt");
    //vector<string> file_vec;
    //getFilePath(argv[1],file_vec);
    //for(vector<string>::iterator iter=file_vec.begin();iter!=file_vec.end();iter++)
    //{
    //    cout<<*iter<<endl;
    //}
    //cout<<LogOrGZFile(argv[1])<<endl;
    
    return 0;
}
