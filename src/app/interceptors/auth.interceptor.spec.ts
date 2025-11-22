import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { Auth.interceptor } from './auth.interceptor';

describe('Auth.interceptor', () => {
  let component: Auth.interceptor;
  let fixture: ComponentFixture<Auth.interceptor>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        Auth.interceptor,
        HttpClientTestingModule
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(Auth.interceptor);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
