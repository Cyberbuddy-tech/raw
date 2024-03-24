import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, Menu
import requests
import json

class RestAPITestApp:
    def __init__(self, root):
        self.root = root
        self.root.title("REST API Test")
        self.root.geometry("800x600")
        self.create_widgets()

    def create_widgets(self):
        self.raw_data_label = ttk.Label(self.root, text="Enter Raw HTTP Request:")
        self.raw_data_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.raw_data_text = scrolledtext.ScrolledText(self.root, width=80, height=10)
        self.raw_data_text.grid(row=0, column=1, columnspan=3, padx=5, pady=5, sticky="nsew")

        self.send_button = ttk.Button(self.root, text="Send Request", command=self.send_request, style='Send.TButton')
        self.send_button.grid(row=1, column=1, padx=5, pady=5)

        self.paste_button = ttk.Button(self.root, text="Paste", command=self.paste_data, style='Paste.TButton')
        self.paste_button.grid(row=1, column=2, padx=5, pady=5)

        self.clear_button = ttk.Button(self.root, text="Clear", command=self.clear_fields, style='Clear.TButton')
        self.clear_button.grid(row=1, column=3, padx=5, pady=5)

        self.response_label = ttk.Label(self.root, text="Response Headers:")
        self.response_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.headers_text = scrolledtext.ScrolledText(self.root, width=60, height=15)
        self.headers_text.grid(row=3, column=0, padx=5, pady=5, sticky="nsew")

        self.response_label = ttk.Label(self.root, text="Response Data:")
        self.response_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.response_text = scrolledtext.ScrolledText(self.root, width=60, height=15)
        self.response_text.grid(row=3, column=1, padx=5, pady=5, sticky="nsew")

        self.root.grid_rowconfigure(3, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.create_menu()

    def create_menu(self):
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.exit_app)
        menubar.add_cascade(label="File", menu=file_menu)

        copy_menu = Menu(menubar, tearoff=0)
        copy_menu.add_command(label="Python Request", command=self.copy_python_request)
        copy_menu.add_command(label="PHP Curl Request", command=self.copy_php_curl_request)
        copy_menu.add_command(label="JavaScript Request", command=self.copy_js_request)
        copy_menu.add_command(label="Go Request", command=self.copy_go_request)
        menubar.add_cascade(label="Copy Request As", menu=copy_menu)

    def send_request(self):
        try:
            raw_data = self.raw_data_text.get("1.0", tk.END).strip()
            lines = raw_data.split("\n")
            method, url, protocol = lines[0].split(" ")
            headers, body = {}, []
            host = None
            
            for line in lines[1:]:
                if line.strip() == "":
                    body = lines[lines.index(line) + 1:]
                    break
                else:
                    header, value = line.split(": ", 1)
                    headers[header] = value
                    if header.lower() == "host":
                        host = value

            if host:
                url = f"https://{host}{url}"

            response = getattr(requests, method.lower())(url, headers=headers, data="\n".join(body))

            self.headers_text.delete("1.0", tk.END)
            self.headers_text.insert(tk.END, "\n".join([f"{key}: {value}" for key, value in response.headers.items()]))
            self.response_text.delete("1.0", tk.END)
            self.response_text.insert(tk.END, response.text)

            try:
                decoded_response = json.loads(response.text)
                self.response_text.delete("1.0", tk.END)
                self.response_text.insert(tk.END, json.dumps(decoded_response, indent=4))
            except json.JSONDecodeError:
                pass

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def paste_data(self):
        try:
            clipboard_data = self.root.clipboard_get()
            self.raw_data_text.insert(tk.END, clipboard_data)
        except tk.TclError:
            messagebox.showerror("Error", "Clipboard is empty.")

    def clear_fields(self):
        self.raw_data_text.delete("1.0", tk.END)
        self.headers_text.delete("1.0", tk.END)
        self.response_text.delete("1.0", tk.END)

    def copy_python_request(self):
        try:
            raw_data = self.raw_data_text.get("1.0", tk.END)
            method, path, _ = raw_data.strip().split("\n")[0].split(" ")
            host = path.split("/")[2]
            url = f"{path.split(' ')[2]}"
            messagebox.showinfo("Python Request", f"""import requests 
                            url = '{url}'
                            headers = {{ {self._format_headers()} }}
                            response = requests.{self._get_method()}(url, headers=headers)""")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def copy_php_curl_request(self):
        try:
            raw_data = self.raw_data_text.get("1.0", tk.END)
            url = raw_data.strip().split("\n")[0].split(" ")[1]
            headers = self._format_headers()
            host = headers.get('Host', None)  # Corrected 'Host' instead of 'host'

            if host:
                php_curl_request = f"""$ch = curl_init();
                curl_setopt($ch, CURLOPT_URL, '{url}');
                curl_setopt($ch,CURLOPT_RETURNTRANSFER, true);
                curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
                curl_setopt($ch, CURLOPT_HTTPHEADER, array({headers}));
                $response = curl_exec($ch);
                curl_close($ch);
                echo $response;"""

                self._copy_to_clipboard(php_curl_request)
            else:
                messagebox.showerror("Error", "Host not found in headers.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")


    def copy_js_request(self):
        try:
            raw_data = self.raw_data_text.get("1.0", tk.END)
            method, url, protocol = raw_data.strip().split("\n")[0].split(" ")
            headers = self._format_headers()
            js_request = f"""var xhr = new XMLHttpRequest();
            xhr.open('{method}', '{url}', true);
            {headers}            xhr.onreadystatechange = function () {{
                if (xhr.readyState == 4 && xhr.status == 200) {{
                    console.log(xhr.responseText);
                }}
            }};
            xhr.send();"""
            self._copy_to_clipboard(js_request)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def copy_go_request(self):
        try:
            raw_data = self.raw_data_text.get("1.0", tk.END)
            method, url, protocol = raw_data.strip().split("\n")[0].split(" ")
            headers = self._format_headers()
            go_request = f"""package main
            import (
                "fmt"
                "net/http"
            )
            func main() {{
                req, _ := http.NewRequest("{method}", "{url}", nil)
                {headers}
                res, _ := http.DefaultClient.Do(req)
                defer res.Body.Close()
                fmt.Println("response Status:", res.Status)
                fmt.Println("response Headers:", res.Header)
                body, _ := ioutil.ReadAll(res.Body)
                fmt.Println("response Body:", string(body))
            }}"""
            self._copy_to_clipboard(go_request)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _format_headers(self):
        headers_str = self.headers_text.get("1.0", tk.END)
        headers = []
        for line in headers_str.strip().split("\n"):
            header, value = line.split(": ", 1)
            headers.append(f'    "{header}": "{value}",')
        return "\n".join(headers)

    def _get_method(self):
        raw_data = self.raw_data_text.get("1.0", tk.END)
        method = raw_data.strip().split("\n")[0].split(" ")[0].lower()
        return method

    def _copy_to_clipboard(self, data):
        self.root.clipboard_clear()
        self.root.clipboard_append(data)
        messagebox.showinfo("Copy to Clipboard", "Request copied to clipboard.")

    def exit_app(self):
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = RestAPITestApp(root)

    # Define styles for buttons
    style = ttk.Style()
    style.configure('Send.TButton', background='#4CAF50')
    style.configure('Paste.TButton', background='#2196F3')
    style.configure('Clear.TButton', background='#FF5722')

    root.mainloop()
