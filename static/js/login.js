(function () {
    const form = document.getElementById('login-form');
    const username = document.getElementById('username');
    const password = document.getElementById('password');
    const toggle = document.getElementById('toggle-password');
    const submit = document.getElementById('login-submit');
    const usernameError = document.getElementById('username-error');
    const passwordError = document.getElementById('password-error');

    if (!form || !username || !password || !submit) {
        return;
    }

    function setError(input, box, message) {
        const field = input.closest('.login-field');
        if (message) {
            field.classList.add('is-invalid');
            input.setAttribute('aria-invalid', 'true');
            box.hidden = false;
            box.textContent = message;
            return;
        }
        field.classList.remove('is-invalid');
        input.removeAttribute('aria-invalid');
        box.hidden = true;
        box.textContent = '';
    }

    function validar() {
        let ok = true;
        if (!username.value.trim()) {
            setError(username, usernameError, 'Informe o usuário.');
            ok = false;
        } else {
            setError(username, usernameError, '');
        }
        if (!password.value) {
            setError(password, passwordError, 'Informe a senha.');
            ok = false;
        } else {
            setError(password, passwordError, '');
        }
        return ok;
    }

    if (toggle) {
        toggle.addEventListener('click', function () {
            const visivel = password.type === 'text';
            password.type = visivel ? 'password' : 'text';
            toggle.setAttribute('aria-pressed', String(!visivel));
            toggle.setAttribute('aria-label', visivel ? 'Mostrar senha' : 'Ocultar senha');
            const icone = toggle.querySelector('i');
            if (icone) {
                icone.className = visivel ? 'bi bi-eye' : 'bi bi-eye-slash';
            }
            password.focus();
        });
    }

    username.addEventListener('input', function () {
        if (username.value.trim()) {
            setError(username, usernameError, '');
        }
    });

    password.addEventListener('input', function () {
        if (password.value) {
            setError(password, passwordError, '');
        }
    });

    form.addEventListener('submit', function (event) {
        if (!validar()) {
            event.preventDefault();
            if (!username.value.trim()) {
                username.focus();
            } else {
                password.focus();
            }
            return;
        }

        submit.disabled = true;
        submit.classList.add('is-loading');
        const loading = submit.querySelector('.login-submit__loading');
        if (loading) {
            loading.hidden = false;
        }
    });
})();
