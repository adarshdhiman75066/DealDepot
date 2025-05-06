document.addEventListener("DOMContentLoaded", function () {
    loadEmployees(); // Load employee list on page load

    // Handle form submission (Add Employee)
    document.getElementById("employeeForm").addEventListener("submit", async function (event) {
        event.preventDefault();

        let empCode = document.getElementById("emp_code").value.trim();
        let name = document.getElementById("name").value.trim();
        let doj = document.getElementById("doj").value.trim();

        if (!empCode || !name || !doj) {
            alert("Please fill all fields!");
            return;
        }

        let requestData = new FormData();
        requestData.append("emp_code", empCode);
        requestData.append("name", name);
        requestData.append("doj", doj);

        let response = await fetch("/api/employees", {
            method: "POST",
            body: requestData
        });

        let result = await response.json();
        alert(result.message);

        if (response.ok) {
            document.getElementById("employeeForm").reset();
            loadEmployees(); // Reload the employee list after adding
        }
    });

    // Load Employees from API
    async function loadEmployees() {
        let response = await fetch("/api/employees");
        let employees = await response.json();
        let employeeTable = document.getElementById("employeeTableBody");
        employeeTable.innerHTML = "";

        employees.forEach(emp => {
            let row = `<tr>
                <td>${emp.emp_code}</td>
                <td>${emp.name}</td>
                <td>${emp.doj}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteEmployee('${emp.emp_code}')" style="background-color: #e94a2d;">Delete</button>
                </td>
            </tr>`;
            employeeTable.innerHTML += row;
        });
    }

    // Delete Employee Function
    window.deleteEmployee = async function(empCode) {
        if (confirm("Are you sure you want to delete this employee?")) {
            let response = await fetch(`/api/employees/${empCode}`, { method: "DELETE" });
            let result = await response.json();
            alert(result.message);
            loadEmployees(); // Reload the table after deletion
        }
    };
});
