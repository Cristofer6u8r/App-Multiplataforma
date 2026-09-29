import tkinter as tk
from tkinter import ttk, messagebox
from models.task import Task
from services.task_repository import TaskRepository

class PlanificaXLite(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PlanificaX Lite - Gestor Académico")
        self.geometry("900x600")
        self.minsize(760, 500)
        self.repo = TaskRepository()
        self.tasks = self.repo.load()
        self.filtered_tasks = []
        self.subject_var = tk.StringVar()
        self.title_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Media")
        self.search_var = tk.StringVar()
        self.configure(padx=12, pady=12)
        self._build_style(); self._build_ui(); self._bind_events(); self.refresh()

    def _build_style(self):
        style = ttk.Style(self)
        try: style.theme_use("clam")
        except tk.TclError: pass
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def _build_ui(self):
        self.columnconfigure(0, weight=1); self.rowconfigure(4, weight=1)
        ttk.Label(self, text="PlanificaX Lite", style="Title.TLabel").grid(row=0,column=0,sticky="w")
        ttk.Label(self, text="Gestor académico multiplataforma • funciona sin Internet").grid(row=1,column=0,sticky="w",pady=(0,12))
        form=ttk.LabelFrame(self,text="Nueva tarea",padding=10); form.grid(row=2,column=0,sticky="ew",pady=(0,10))
        form.columnconfigure(1,weight=1); form.columnconfigure(3,weight=1)
        ttk.Label(form,text="Materia:").grid(row=0,column=0,sticky="w",padx=(0,6))
        ttk.Entry(form,textvariable=self.subject_var).grid(row=0,column=1,sticky="ew",padx=(0,12))
        ttk.Label(form,text="Tarea:").grid(row=0,column=2,sticky="w",padx=(0,6))
        ttk.Entry(form,textvariable=self.title_var).grid(row=0,column=3,sticky="ew",padx=(0,12))
        ttk.Label(form,text="Prioridad:").grid(row=1,column=0,sticky="w",pady=(8,0))
        ttk.Combobox(form,textvariable=self.priority_var,values=("Baja","Media","Alta"),state="readonly",width=12).grid(row=1,column=1,sticky="w",pady=(8,0))
        ttk.Button(form,text="Agregar tarea",command=self.add_task).grid(row=1,column=3,sticky="e",pady=(8,0))
        toolbar=ttk.Frame(self); toolbar.grid(row=3,column=0,sticky="new",pady=(0,8)); toolbar.columnconfigure(1,weight=1)
        ttk.Label(toolbar,text="Buscar:").grid(row=0,column=0,padx=(0,6))
        ttk.Entry(toolbar,textvariable=self.search_var).grid(row=0,column=1,sticky="ew")
        ttk.Button(toolbar,text="Marcar completada",command=self.complete_selected).grid(row=0,column=2,padx=(8,4))
        ttk.Button(toolbar,text="Eliminar",command=self.delete_selected).grid(row=0,column=3)
        table=ttk.Frame(self); table.grid(row=4,column=0,sticky="nsew"); table.columnconfigure(0,weight=1); table.rowconfigure(0,weight=1)
        cols=("materia","tarea","prioridad","estado")
        self.tree=ttk.Treeview(table,columns=cols,show="headings",selectmode="browse")
        for c,t in zip(cols,("Materia","Tarea","Prioridad","Estado")): self.tree.heading(c,text=t)
        self.tree.column("materia",width=180); self.tree.column("tarea",width=390); self.tree.column("prioridad",width=100,anchor="center"); self.tree.column("estado",width=120,anchor="center")
        scroll=ttk.Scrollbar(table,orient="vertical",command=self.tree.yview); self.tree.configure(yscrollcommand=scroll.set)
        self.tree.grid(row=0,column=0,sticky="nsew"); scroll.grid(row=0,column=1,sticky="ns")
        self.status_var=tk.StringVar(); ttk.Label(self,textvariable=self.status_var).grid(row=5,column=0,sticky="w",pady=(8,0))
        ttk.Label(self,text="Atajos: Ctrl+N agrega • Enter completa • Delete elimina").grid(row=6,column=0,sticky="w",pady=(4,0))

    def _bind_events(self):
        self.search_var.trace_add("write",lambda *_: self.refresh())
        self.bind("<Control-n>",lambda e:self.add_task()); 
        self.bind("<Return>",lambda e:self.complete_selected()); 
        self.bind("<Delete>",lambda e:self.delete_selected())

    def add_task(self):
        subject=self.subject_var.get().strip(); title=self.title_var.get().strip()
        if not subject or not title:
            messagebox.showwarning("Datos incompletos","Escribe la materia y el nombre de la tarea."); return
        self.tasks.append(Task(subject,title,self.priority_var.get()))
        self.repo.save(self.tasks); self.subject_var.set(""); self.title_var.set(""); self.priority_var.set("Media"); self.refresh()
        messagebox.showinfo("Tarea agregada","La tarea se guardó correctamente.")

    def selected_task(self):
        sel=self.tree.selection()
        if not sel:
            messagebox.showwarning("Selección","Selecciona una tarea de la lista."); return None
        idx=int(self.tree.item(sel[0],"values")[4]); return self.filtered_tasks[idx]

    def complete_selected(self):
        task=self.selected_task()
        if task is None: return
        task.completed=not task.completed; self.repo.save(self.tasks); self.refresh()

    def delete_selected(self):
        task=self.selected_task()
        if task is None: return
        if not messagebox.askyesno("Confirmar",f"¿Eliminar la tarea '{task.title}'?"): return
        self.tasks.remove(task); self.repo.save(self.tasks); self.refresh()

    def refresh(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        q=self.search_var.get().strip().lower()
        self.filtered_tasks=[t for t in self.tasks if q in t.subject.lower() or q in t.title.lower()]
        for idx,t in enumerate(self.filtered_tasks):
            self.tree.insert("","end",values=(t.subject,t.title,t.priority,"Completada" if t.completed else "Pendiente",idx))
        total=len(self.tasks); done=sum(1 for t in self.tasks if t.completed)
        self.status_var.set(f"Total: {total}   •   Completadas: {done}   •   Pendientes: {total-done}")

if __name__ == "__main__": PlanificaXLite().mainloop()
